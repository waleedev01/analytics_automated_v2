import unittest
import logging
import yaml
import os
from analytics_automated.cwl_utils.cwl_schema_validator import CWLSchemaValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestCWLSchemaValidator(unittest.TestCase):

    def setUp(self):
        """Setup the CWLSchemaValidator instance for testing."""
        self.validator = CWLSchemaValidator()
        self.test_files_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

    def load_cwl_file(self, filename):
        """Load a CWL file from the fixtures directory."""
        filepath = os.path.join(self.test_files_dir, filename)
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    
    def get_cwl_file_path(self, filename):
        """Get the path to a CWL file in the fixtures directory."""
        return os.path.join(self.test_files_dir, filename)

    def test_validate_cwl_valid_workflow(self):
        """Test validation of a valid CWL workflow."""
        valid_workflow = self.load_cwl_file('valid_workflow.cwl')
        is_valid, message = self.validator.validate_cwl(valid_workflow)
        self.assertTrue(is_valid)
        self.assertEqual(message, "CWL file is valid.")
    
    def test_validate_cwl_valid_workflow_from_file(self):
        """Test validation of a valid CWL workflow from a file path."""
        valid_workflow_path = self.get_cwl_file_path('valid_workflow.cwl')
        is_valid, message = self.validator.validate_cwl(valid_workflow_path)
        self.assertTrue(is_valid)
        self.assertEqual(message, "CWL file is valid.")

    def test_validate_cwl_valid_workflow_with_optional_fields(self):
        """Test validation of a valid CWL workflow with optional fields."""
        valid_workflow = self.load_cwl_file('valid_workflow_with_optional_fields.cwl')
        is_valid, message = self.validator.validate_cwl(valid_workflow)
        self.assertTrue(is_valid)
        self.assertEqual(message, "CWL file is valid.")

    def test_validate_cwl_invalid_arguments(self):
        """Test validation of a CWL CommandLineTool with invalid 'arguments'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_invalid_arguments.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("'arguments' must be a list", message)

    def test_validate_cwl_invalid_stdin(self):
        """Test validation of a CWL CommandLineTool with invalid 'stdin'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_invalid_stdin.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("'stdin' must be a string", message)

    def test_validate_cwl_invalid_stdout(self):
        """Test validation of a CWL CommandLineTool with invalid 'stdout'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_invalid_stdout.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("'stdout' must be a string", message)

    def test_validate_cwl_invalid_stderr(self):
        """Test validation of a CWL CommandLineTool with invalid 'stderr'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_invalid_stderr.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("'stderr' must be a string", message)

    def test_validate_cwl_missing_version(self):
        """Test validation of a CWL file missing 'cwlVersion'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_version.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'cwlVersion' in CWL file", message)

    def test_validate_cwl_unsupported_version(self):
        """Test validation of a CWL file with an unsupported 'cwlVersion'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_unsupported_version.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported CWL version: v2.0", message)

    def test_validate_cwl_missing_class(self):
        """Test validation of a CWL file missing 'class'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_class.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'class' in CWL file", message)

    def test_validate_cwl_unsupported_class(self):
        """Test validation of a CWL file with an unsupported 'class'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_unsupported_class.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported class: UnsupportedClass", message)

    def test_validate_cwl_unsupported_requirement(self):
        """Test validation of a CWL file with unsupported requirements."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_unsupported_requirement.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported requirement: DockerRequirement", message)

    def test_validate_cwl_non_list_requirements(self):
        """Test validation of a CWL file with 'requirements' not as a list."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_non_list_requirements.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Please define requirements in CWL as list", message) 


    def test_validate_cwl_valid_requirements(self):
        """Test validation of a CWL file with a valid 'requirements' list."""
        valid_workflow = self.load_cwl_file('valid_workflow_requirements.cwl')
        is_valid, message = self.validator.validate_cwl(valid_workflow)
        self.assertTrue(is_valid)
        self.assertEqual(message, "CWL file is valid.")

    def test_validate_cwl_missing_inputs(self):
        """Test validation of a CWL file missing 'inputs'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_inputs.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'inputs' in CWL file", message)

    def test_validate_cwl_missing_outputs(self):
        """Test validation of a CWL file missing 'outputs'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_outputs.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'outputs' in CWL file", message)

    def test_validate_cwl_missing_steps(self):
        """Test validation of a CWL workflow missing 'steps'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_steps.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'steps' in CWL file", message)

    def test_validate_cwl_missing_run_in_steps(self):
        """Test validation of a CWL workflow with steps missing 'run'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_run_in_steps.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'run' for step 'step1'", message)

    def test_validate_cwl_missing_in_in_steps(self):
        """Test validation of a CWL workflow with steps missing 'in'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_in_in_steps.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'in' for step 'step1'", message)

    def test_validate_cwl_missing_out_in_steps(self):
        """Test validation of a CWL workflow with steps missing 'out'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_out_in_steps.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'out' for step 'step1'", message)

    def test_validate_cwl_invalid_base_command(self):
        """Test validation of a CWL CommandLineTool with an invalid 'baseCommand'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_invalid_base_command.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Validation failed: 'baseCommand' must be a string or list of strings", message)

    def test_validate_cwl_generic_exception(self):
        """Test validation that raises a generic exception."""
        # Use an invalid data type to trigger a generic exception
        invalid_workflow = self.load_cwl_file('invalid_workflow_generic_exception.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Validation failed", message)

    def test_validate_cwl_non_list_hints(self):
        """Test validation of a CWL file with 'hints' not as a list."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_non_list_hints.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Please define hints in CWL as list", message)
    
    def test_validate_cwl_unsupported_hint(self):
        """Test validation of a CWL file with unsupported hints."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_unsupported_hint.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported hint: DockerRequirement", message)

    def test_validate_cwl_missing_input_type(self):
        """Test validation of a CWL file with missing 'type' in inputs."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_input_type.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'type' for input 'input1'", message)

    def test_validate_cwl_missing_output_type(self):
        """Test validation of a CWL file with missing 'type' in outputs."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_output_type.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'type' for output 'output1'", message)

    def test_validate_cwl_missing_base_command(self):
        """Test validation of a CWL CommandLineTool missing 'baseCommand'."""
        invalid_workflow = self.load_cwl_file('invalid_workflow_missing_base_command.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'baseCommand' in CommandLineTool", message)

    def test_validate_cwl_invalid_file_path(self):
        """Test validation of an invalid CWL file path."""
        invalid_workflow_path = self.get_cwl_file_path('non_existent_file.cwl')
        is_valid, message = self.validator.validate_cwl(invalid_workflow_path)
        self.assertFalse(is_valid)
        self.assertIn("Validation failed", message)

if __name__ == '__main__':
    unittest.main()
