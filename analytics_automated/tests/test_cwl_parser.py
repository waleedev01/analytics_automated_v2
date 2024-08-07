import os
import yaml
from django.test import TestCase
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
from analytics_automated.models import Backend
from analytics_automated.cwl_utils.cwl_schema_validator import CWLSchemaValidator

def add_fake_backend(name, root_path):
    b = Backend.objects.create(name=name)
    b.root_path = root_path
    b.save()
    return b

class CWLParserTest(TestCase):
    def test_read_cwl_file(self):
        """
        Test if the CWL file is read correctly.
        """
        this_backend = add_fake_backend(name="local1", root_path="/tmp/")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # filenames = ['task1', 'task2', 'task3', 'task4', 'workflow']
        filenames = ['create_fasta_S01', 'run_legacy_psiblast_S1']
        message = []
        for filename in filenames:
            file_path = os.path.join(base_dir, 'tests', 'example_cwl_files', f'{filename}.cwl')
            read_cwl_file(file_path, filename, message)
            print(f"[{filename} Message]", message[-1])
        # result = read_cwl_file(file_path, filename, message)
        # self.assertIsNotNone(result)

    def tearDown(self):
        pass

class CWLValidatorTest(TestCase):
    def test_validate_cwl(self):
        """
        Test the CWL schema validator.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'tests', 'example_cwl_files', 's4pred_workflow.cwl')
        with open(file_path, 'r') as cwl_file:
            cwl_data = yaml.safe_load(cwl_file)
        validator = CWLSchemaValidator()
        is_valid, message = validator.validate_cwl(cwl_data)
        self.assertTrue(is_valid, message)

    def test_invalid_cwl(self):
        """
        Test the CWL schema validator with an invalid CWL file.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'tests', 'example_cwl_files', 'invalid_workflow.cwl')
        with open(file_path, 'r') as cwl_file:
            cwl_data = yaml.safe_load(cwl_file)
        validator = CWLSchemaValidator()
        is_valid, message = validator.validate_cwl(file_path)
        self.assertFalse(is_valid, message)

    def tearDown(self):
        pass