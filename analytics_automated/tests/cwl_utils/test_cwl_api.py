import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from analytics_automated.models import Job, Task, Step, Backend
import zipfile
import io

class CWLAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.upload_url = '/analytics_automated/uploadcwl/'
        self.download_url = '/analytics_automated/downloadcwl/'
        
        self.backend = Backend.objects.create(name="Test Backend", root_path="/tmp/")
        self.test_job = Job.objects.create(name="test_job", runnable=True)
        self.test_task = Task.objects.create(
            backend=self.backend,
            name="test_task",
            in_glob=".input",
            out_glob=".output",
            executable="echo"
        )
        Step.objects.create(job=self.test_job, task=self.test_task, ordering=0)

        self.workflow_content = """
        cwlVersion: v1.0
        class: Workflow
        inputs: []
        outputs: []
        steps: {}
        """
        self.commandlinetool_content = """
        cwlVersion: v1.0
        class: CommandLineTool
        baseCommand: echo
        inputs: []
        outputs: []
        """

    def tearDown(self):
        Job.objects.all().delete()
        Task.objects.all().delete()
        Step.objects.all().delete()
        Backend.objects.all().delete()

    # Upload API Tests

    def test_upload_single_workflow(self):
        file = SimpleUploadedFile("workflow.cwl", self.workflow_content.encode())
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('workflow.cwl', response.data['file_names'])

    def test_upload_no_files(self):
        response = self.client.post(self.upload_url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('files', response.data)
        self.assertIn('This field is required.', str(response.data['files']))

    def test_upload_non_cwl_file(self):
        file = SimpleUploadedFile("not_cwl.txt", b"This is not a CWL file")
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Skipped non-CWL file: not_cwl.txt", response.data['messages'])

    def test_upload_invalid_yaml(self):
        invalid_yaml = """
        cwlVersion: v1.0
        class: Workflow
        inputs: [
        outputs: []
        steps: {}
        """
        file = SimpleUploadedFile("invalid_yaml.cwl", invalid_yaml.encode())
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Error parsing YAML in file invalid_yaml.cwl", response.data['messages'][0])

    def test_upload_non_dict_cwl(self):
        non_dict_cwl = "This is not a dictionary"
        file = SimpleUploadedFile("non_dict.cwl", non_dict_cwl.encode())
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid CWL format in file: non_dict.cwl", response.data['messages'][0])

    def test_upload_invalid_cwl_class(self):
        invalid_content = """
        cwlVersion: v1.0
        class: InvalidClass
        inputs: []
        outputs: []
        """
        file = SimpleUploadedFile("invalid_class.cwl", invalid_content.encode())
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("File invalid_class.cwl is not a Workflow or CommandLineTool", str(response.data))

    @patch('analytics_automated.cwl_utils.cwl_api.read_cwl_file')
    def test_upload_general_exception(self, mock_read_cwl):
        mock_read_cwl.side_effect = Exception("General error")
        file = SimpleUploadedFile("error.cwl", self.workflow_content.encode())
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['error'], "Error processing CWL files")
        self.assertIn("General error", str(response.data['detail']))


    @patch('analytics_automated.cwl_utils.cwl_api.read_cwl_file')
    def test_upload_read_cwl_file_error(self, mock_read_cwl):
        mock_read_cwl.side_effect = Exception("Error reading CWL file")
        file = SimpleUploadedFile("error.cwl", self.workflow_content.encode())
        response = self.client.post(self.upload_url, {'files': [file]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Error reading CWL file", str(response.data['detail']))

    # Download API Tests

    def test_download_existing_job(self):
        with patch('analytics_automated.cwl_utils.cwl_api.reconstruct_cwl_files') as mock_reconstruct:
            def side_effect(job_name, output_directory):
                with open(os.path.join(output_directory, 'test.cwl'), 'w') as f:
                    f.write(self.workflow_content)

            mock_reconstruct.side_effect = side_effect

            response = self.client.get(f"{self.download_url}?job_name=test_job")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'application/zip')
            self.assertEqual(response['Content-Disposition'], 'attachment; filename="test_job_cwl.zip"')

            content = b''.join(response.streaming_content)
            with io.BytesIO(content) as temp_file:
                with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                    self.assertIn('test.cwl', zip_ref.namelist())

    def test_download_non_existing_job(self):
        response = self.client.get(f"{self.download_url}?job_name=non_existing_job")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download_without_job_name(self):
        response = self.client.get(self.download_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('analytics_automated.cwl_utils.cwl_api.reconstruct_cwl_files')
    def test_download_with_error(self, mock_reconstruct):
        mock_reconstruct.side_effect = Exception("Test error")
        response = self.client.get(f"{self.download_url}?job_name=test_job")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('analytics_automated.cwl_utils.cwl_api.tempfile.TemporaryDirectory')
    def test_download_temp_dir_error(self, mock_temp_dir):
        mock_temp_dir.side_effect = OSError("Failed to create temp directory")
        response = self.client.get(f"{self.download_url}?job_name=test_job")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Failed to generate CWL files", str(response.data['error']))

    @patch('analytics_automated.cwl_utils.cwl_api.zipfile.ZipFile')
    def test_download_zip_file_error(self, mock_zipfile):
        mock_zipfile.side_effect = Exception("Zip file error")
        response = self.client.get(f"{self.download_url}?job_name=test_job")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Failed to generate CWL files", str(response.data['error']))

    @patch('analytics_automated.cwl_utils.cwl_api.open')
    def test_download_file_open_error(self, mock_open):
        mock_open.side_effect = IOError("File open error")
        response = self.client.get(f"{self.download_url}?job_name=test_job")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Failed to generate CWL files", str(response.data['error']))