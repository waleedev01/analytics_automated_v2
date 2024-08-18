import logging
import yaml
import tempfile
import os
import zipfile

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from ..serializers import CWLUploadSerializer, CWLDownloadSerializer
from ..models import Job
from .cwl_parser import read_cwl_file
from .reconstruct_cwl import reconstruct_cwl_files

logger = logging.getLogger(__name__)

class CWLUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        Upload and process CWL files.

        This endpoint allows users to upload CWL files for processing.
        It validates the files, processes them, and returns the results.
        Accepts both Workflow and CommandLineTool CWL files.

        Request body:
        - files: List of CWL files to upload and process

        Returns:
        - 201 Created: If files are successfully processed
        - 400 Bad Request: If no files are provided or if files are invalid
        - 500 Internal Server Error: If there's an error during processing
        """
        serializer = CWLUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('files')
        if not files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        messages = []
        valid_cwl_files = {}

        for file in files:
            logger.info(f"Processing file: {file.name}")
            if not file.name.endswith('.cwl'):
                messages.append(f"Skipped non-CWL file: {file.name}")
                continue

            try:
                if isinstance(file, TemporaryUploadedFile):
                    file_path = file.temporary_file_path()
                else:
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        for chunk in file.chunks():
                            temp_file.write(chunk)
                        file_path = temp_file.name

                with open(file_path, 'r') as cwl_file:
                    cwl_data = yaml.safe_load(cwl_file)
                
                if not isinstance(cwl_data, dict):
                    messages.append(f"Invalid CWL format in file: {file.name}")
                    continue
                
                cwl_class = cwl_data.get("class")
                if cwl_class not in ["Workflow", "CommandLineTool"]:
                    messages.append(f"File {file.name} is not a Workflow or CommandLineTool (class: {cwl_class})")
                    continue
                
                valid_cwl_files[file.name] = cwl_data

            except yaml.YAMLError as e:
                messages.append(f"Error parsing YAML in file {file.name}: {str(e)}")
            except Exception as e:
                messages.append(f"Error processing file {file.name}: {str(e)}")
            finally:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.unlink(file_path)

        if not valid_cwl_files:
            return Response({
                "error": "No valid CWL files found", 
                "messages": messages
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            for cwl_name, cwl_data in valid_cwl_files.items():
                filename = os.path.splitext(cwl_name)[0]
                read_cwl_file(filename, cwl_data, messages)

            return Response({
                "message": "CWL files processed successfully",
                "file_names": list(valid_cwl_files.keys()),
                "messages": messages
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception(f"Error processing CWL files: {str(e)}")
            return Response({
                "error": "Error processing CWL files",
                "detail": str(e),
                "messages": messages
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CWLDownloadView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Download CWL files for a specified job.

        This endpoint allows users to download CWL files for a given job.
        It reconstructs the CWL files and returns them as a zip archive.

        Query parameters:
        - job_name: Name of the job to download CWL files for

        Returns:
        - ZIP file containing CWL files if successful
        - 400 Bad Request: If no job name is provided
        - 404 Not Found: If the specified job doesn't exist
        - 500 Internal Server Error: If there's an error during file generation
        """
        serializer = CWLDownloadSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        job_name = serializer.validated_data['job_name']

        try:
            job = Job.objects.get(name=job_name)
        except Job.DoesNotExist:
            logger.warning(f"Attempted to download non-existent job: {job_name}")
            return Response({"error": f"Job '{job_name}' does not exist"}, 
                            status=status.HTTP_404_NOT_FOUND)

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                reconstruct_cwl_files(job_name, temp_dir)
                zip_file_path = os.path.join(temp_dir, f"{job_name}_cwl.zip")

                with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname=arcname)

                response = FileResponse(open(zip_file_path, 'rb'), 
                                        content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{job_name}_cwl.zip"'
                return response

        except Exception as e:
            logger.exception(f"Error generating CWL files for job '{job_name}': {str(e)}")
            return Response({
                "error": "Failed to generate CWL files",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)