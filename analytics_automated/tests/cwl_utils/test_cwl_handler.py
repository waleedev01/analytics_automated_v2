import unittest
import logging
import yaml
import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'analytics_automated_project.settings.dev'
django.setup()
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
from analytics_automated.models import Backend, Parameter, QueueType, Step, Task
from analytics_automated.tests.helper_functions import clearDatabase


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def add_fake_backend(name, root_path):
    """
    Create or update a Backend with a specific name and root path.

    Args:
        name (str): The name of the Backend.
        root_path (str): The root path for the Backend.

    Returns:
        Backend: The Backend instance created or updated.
    """
    # check if a Backend with ID 1 exists
    try:
        b = Backend.objects.get(id=1)
    except Backend.DoesNotExist:
        # get or create a QueueType
        q = QueueType.objects.all().first()
        if q is None:
            q = QueueType.objects.create(name="localhost", execution_behaviour=QueueType.LOCALHOST)
        
        # create a new Backend and set its ID to 1
        b = Backend.objects.create(name=name, queue_type=q, root_path=root_path)
        Backend.objects.filter(id=b.id).update(id=1)
        b = Backend.objects.get(id=1)
    
    b.root_path = root_path
    b.save()
    
    return b

class TestCWLCLTParser(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test case is run.
        """
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.backend = add_fake_backend(name="local1", root_path="/tmp/")


    def load_cwl_file(self, filename):
        """
        Generate the full path to a CWL file in the fixtures directory.

        Args:
            filename (str): The name of the CWL file.

        Returns:
            str: The full path to the CWL file.
        """
        return os.path.join(self.test_files_dir, filename)

    def test_parse_cwl_clt_valid(self):
        """
        Test the parsing of a valid CWL CommandLineTool.

        Verifies that the CWL CommandLineTool is parsed correctly, checking attributes such 
        as name, input and output glob patterns, and executable command.

        Asserts:
            The parsed CommandLineTool is not None.
            The parsed CommandLineTool attributes match the expected values.
        """
        filepath = os.path.join(self.test_files_dir, 'some_tool.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'some_tool', messages)
        self.assertIsNotNone(clt)
        self.assertEqual(clt.name, "some_tool")
        self.assertEqual(clt.in_glob, ".input")
        self.assertEqual(clt.out_glob, ".txt")
        self.assertEqual(clt.executable, "echo $I1")
    
    def test_parse_cwl_clt_with_parameters(self):
        """
        Test the parsing of a CWL CommandLineTool with parameters.

        Verifies that the CWL CommandLineTool with parameters is parsed correctly, including 
        the number of parameters associated with the tool.

        Asserts:
            The parsed CommandLineTool is not None.
            The parsed CommandLineTool attributes match the expected values.
            The number of parameters associated with the CommandLineTool is as expected.
        """
        filepath = os.path.join(self.test_files_dir, 'valid_clt_with_parameters.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'valid_clt_with_parameters', messages)
        self.assertIsNotNone(clt)
        self.assertEqual(clt.name, "valid_clt_with_parameters")
        self.assertEqual(clt.in_glob, ".ss")
        self.assertEqual(clt.out_glob, ".txt")
        self.assertEqual(clt.executable, "echo $P1 $P2 $I1")
        params = Parameter.objects.filter(task=clt)
        self.assertEqual(len(params), 2)

    def test_parse_cwl_clt_existing(self):
        """
        Test parsing of an existing CWL CommandLineTool.

        Verifies that parsing the same CWL CommandLineTool twice results in messages indicating 
        that the task already exists.

        Asserts:
            The parsed CommandLineTool is not None.
            The messages include a notification about the existing task.
        """
        filepath = os.path.join(self.test_files_dir, 'some_tool.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'some_tool', messages)
        self.assertIsNotNone(clt)

        messages = []
        clt = read_cwl_file(filepath, 'some_tool', messages)
        self.assertIsNotNone(clt)
        self.assertIn("Found existing task with name: some_tool", messages)
    
    def test_parse_cwl_clt_with_arguments(self):
        """
        Test parsing of a CWL CommandLineTool with arguments.

        Verifies that the CommandLineTool's executable contains the expected arguments.

        Asserts:
            The parsed CommandLineTool is not None.
            The executable command contains specific arguments.
        """
        filepath = os.path.join(self.test_files_dir, 'valid_clt_with_arguments.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'valid_clt_with_arguments', messages)
        self.assertIsNotNone(clt)
        self.assertEqual(clt.name, "valid_clt_with_arguments")
        argument1 = '-graph' in clt.executable
        argument2 = '-window' in clt.executable
        argument3 = '-order' in clt.executable
        self.assertTrue(argument1)
        self.assertTrue(argument2)
        self.assertTrue(argument3)
    
    def test_parse_cwl_clt_invalid_validation(self):
        """
        Test parsing of an invalid CWL CommandLineTool.

        Verifies that invalid CWL data is handled correctly, and appropriate validation 
        failure messages are returned.

        Asserts:
            The parsed CommandLineTool is None.
            The messages include validation failure information.
        """
        filepath = os.path.join(self.test_files_dir, 'invalid_workflow_invalid_arguments.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'invalid_workflow_invalid_arguments', messages)
        self.assertIsNone(clt)
        self.assertIn("Validation Failed: Validation failed: 'arguments' must be a list", messages)
    
    def test_parse_cwl_clt_not_found(self):
        """
        Test parsing of a non-existent CWL CommandLineTool.

        Verifies that a missing CWL file results in the expected behavior, where the 
        CommandLineTool cannot be found.

        Asserts:
            The parsed CommandLineTool is None.
        """
        filepath = os.path.join(self.test_files_dir, 'not_found.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'not_found', messages)
        self.assertIsNone(clt)
    
    def tearDown(self):
        clearDatabase()

class TestCWLWorkflowParser(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment before each test case is executed.

        Initializes the test files directory and creates a fake Backend instance to be used
        in the tests.
        """
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.backend = add_fake_backend(name="local1", root_path="/tmp/")

    def load_cwl_file(self, filename):
        """
        Generate the full path to a CWL file in the fixtures directory.

        Args:
            filename (str): The name of the CWL file.

        Returns:
            str: The full path to the CWL file.
        """
        return os.path.join(self.test_files_dir, filename)

    def test_parse_cwl_workflow_inline_valid(self):
        """
        Test parsing of a valid inline CWL workflow.

        Verifies that the CWL workflow is parsed correctly when all steps are defined inline, 
        and checks the number of steps in the workflow.

        Asserts:
            The parsed workflow is not None.
            The workflow name matches the expected value.
            The number of steps in the workflow is as expected.
        """
        filepath = os.path.join(self.test_files_dir, 'valid_workflow_with_steps.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow_with_steps', messages)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.name, "valid_workflow_with_steps")
        steps = Step.objects.filter(job=workflow)
        self.assertEqual(len(steps), 3)
    
    def test_parse_cwl_workflow_separate_valid(self):
        """
        Test parsing of a valid separate CWL workflow.

        Verifies that the CWL workflow correctly references separate CommandLineTools 
        and that the workflow is parsed as expected.

        Asserts:
            The parsed CommandLineTool is not None.
            The parsed workflow is not None.
            The workflow name matches the expected value.
            The number of steps in the workflow is as expected.
            The messages include the expected task creation information.
        """
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
        """
        Test parsing of an existing CWL workflow.

        Verifies that parsing the same CWL workflow twice results in messages indicating 
        that the job already exists.

        Asserts:
            The parsed workflow is not None.
            The messages include a notification about the existing job.
        """
        filepath = os.path.join(self.test_files_dir, 'valid_workflow_with_steps.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow_with_steps', messages)
        self.assertIsNotNone(workflow)

        messages = []
        workflow = read_cwl_file(filepath, 'valid_workflow_with_steps', messages)
        self.assertIsNotNone(workflow)
        self.assertIn("Found existing job with name: valid_workflow_with_steps", messages)
    
    def test_parse_cwl_workflow_without_existing_task(self):
        """
        Test parsing of a CWL workflow without existing tasks.

        Verifies that a workflow that references non-existent tasks is handled correctly, 
        including appropriate error messages.

        Asserts:
            The parsed workflow is None.
            The messages include information about the missing task file and job creation cancellation.
            The number of messages is as expected.
        """
        filepath = os.path.join(self.test_files_dir, 'not_found_task_workflow.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'not_found_task_workflow', messages)
        self.assertIsNone(workflow)
        self.assertIn("Task file not found: some_tools", messages)
        self.assertIn("Cancel job creation with name 'not_found_task_workflow' due to missing task file: some_tools", messages)
        self.assertEqual(len(messages), 2)
    
    def test_parse_cwl_workflow_circular(self):
        """
        Test parsing of a circular dependency CWL workflow.

        Verifies that a workflow with circular dependencies is handled correctly, including 
        appropriate error messages.

        Asserts:
            The parsed workflow is None.
            The messages include information about the circular dependency and job creation cancellation.
        """
        filepath = os.path.join(self.test_files_dir, 'circular_workflow.cwl')
        messages = []
        workflow = read_cwl_file(filepath, 'circular_workflow', messages)
        self.assertIsNone(workflow)
        self.assertIn("Cancel job creation with name 'circular_workflow' due to circular dependency in step: some_tool_1", messages)
    
    def test_parse_cwl_workflow_invalid_step(self):
        """
        Test parsing of a CWL workflow with an invalid step.

        Verifies that a workflow with an invalid step is handled correctly, including 
        appropriate error messages.

        Asserts:
            The parsed workflow is None.
            The messages include information about the invalid step and job creation cancellation.
        """
        filepath = os.path.join(self.test_files_dir, 'workflow_invalid_steps.cwl')
        messages = []
        clt = read_cwl_file(filepath, 'workflow_invalid_steps', messages)
        self.assertIsNone(clt)
        self.assertIn("Cancel job creation with name 'workflow_invalid_steps' due to failure when creating task file: step1", messages)
    
    def tearDown(self):
        """  Clean up the test environment after each test case is executed. """
        clearDatabase()

if __name__ == '__main__':
    unittest.main()