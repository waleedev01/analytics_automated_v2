import unittest
import logging
import yaml
import os
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
from analytics_automated.models import Backend, Parameter, QueueType, Step, Task
from analytics_automated.tests.helper_functions import clearDatabase

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def add_fake_backend(name, root_path):
    q = QueueType.objects.all().first()
    b = Backend.objects.create(name=name, queue_type=q)
    b.root_path = root_path
    b.save()
    Backend.objects.filter(id=b.id).update(id=1)
    b = Backend.objects.get(id=1)
    return b

class TestCWLCLTParser(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test case is run.
        """
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.backend = add_fake_backend(name="local1", root_path="/tmp/")

    def load_cwl_file(self, filename):
        """Load a CWL file from the fixtures directory."""
        return os.path.join(self.test_files_dir, filename)

    def test_parse_cwl_clt_valid(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'some_tool.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'some_tool', messages)
        self.assertIsNotNone(clt)
        self.assertEqual(clt.name, "some_tool")
        self.assertEqual(clt.out_glob, ".txt")
        self.assertEqual(clt.executable, "echo") # there should be also $I1
    
    def test_parse_cwl_clt_with_parameters(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'valid_clt_with_parameters.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'valid_clt_with_parameters', messages)
        self.assertIsNotNone(clt)
        self.assertEqual(clt.name, "valid_clt_with_parameters")
        self.assertEqual(clt.out_glob, ".txt")
        self.assertEqual(clt.executable, "echo $P1 $P2") # there should be also $I1
        params = Parameter.objects.filter(task=clt)
        self.assertEqual(len(params), 2)

    def test_parse_cwl_clt_existing(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'some_tool.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'some_tool', messages)
        self.assertIsNotNone(clt)

        messages = []
        clt = read_cwl_file(filepath, 'some_tool', messages)
        self.assertIsNotNone(clt)
        self.assertIn("Found existing task with name: some_tool", messages)
    
    def test_parse_cwl_clt_invalid_validation(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'invalid_workflow_invalid_arguments.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'invalid_workflow_invalid_arguments', messages)
        self.assertIsNone(clt)
        self.assertIn("Validation Failed: Validation failed: 'arguments' must be a list", messages)
    
    def test_parse_cwl_clt_not_found(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'not_found.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'not_found', messages)
        self.assertIsNone(clt)
    
    def test_parse_cwl_clt_invalid_validation(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'workflow_invalid_steps.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'workflow_invalid_steps', messages)
        self.assertIsNone(clt)
        self.assertIn("Cancel job creation with name 'workflow_invalid_steps' due to failure when creating task file: step1", messages)
    
    def test_parse_cwl_clt_dynamic_value(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'dynamic_value.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'dynamic_value', messages)
        self.assertIsNotNone(clt)
        self.assertEqual(clt.executable, "echo $ID $TMP/$ID/$I1 $O1")
    
    def tearDown(self):
        clearDatabase()

class TestCWLWorkflowParser(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test case is run.
        """
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.backend = add_fake_backend(name="local1", root_path="/tmp/")

    def load_cwl_file(self, filename):
        """Load a CWL file from the fixtures directory."""
        return os.path.join(self.test_files_dir, filename)

    def test_parse_cwl_workflow_without_existing_task(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'valid_workflow.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow', messages)
        self.assertIsNone(workflow)
        self.assertIn("Task file not found: some_tool", messages)
        self.assertIn("Cancel job creation with name 'valid_workflow' due to missing task file: some_tool", messages)
        self.assertEqual(len(messages), 2)

    def test_parse_cwl_workflow_inline_valid(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'valid_workflow_with_steps.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow_with_steps', messages)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.name, "valid_workflow_with_steps")
        steps = Step.objects.filter(job=workflow)
        self.assertEqual(len(steps), 3)
    
    def test_parse_cwl_workflow_separate_valid(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'separate_clt.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'separate_clt', messages)
        self.assertIsNotNone(clt)

        filepath = os.path.join(self.test_files_dir, 'workflow_separate_clt.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'workflow_separate_clt', messages)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.name, "workflow_separate_clt")
        steps = Step.objects.filter(job=workflow)
        self.assertEqual(len(steps), 1)
        self.assertIn("Job 'workflow_separate_clt' created with tasks: separate_clt", messages)
    
    def test_parse_cwl_workflow_existing(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'valid_workflow_with_steps.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow_with_steps', messages)
        self.assertIsNotNone(workflow)

        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow_with_steps', messages)
        self.assertIsNotNone(workflow)
        self.assertIn("Found existing job with name: valid_workflow_with_steps", messages)
    
    def test_parse_cwl_workflow_circular(self):
        """Test parsing of a valid CWL workflow."""
        filepath = os.path.join(self.test_files_dir, 'circular_workflow.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'circular_workflow', messages)
        self.assertIsNone(workflow)
        self.assertIn("Cancel job creation with name 'circular_workflow' due to circular dependency in step: some_tool_1", messages)
    
    def tearDown(self):
        clearDatabase()

if __name__ == '__main__':
    unittest.main()
