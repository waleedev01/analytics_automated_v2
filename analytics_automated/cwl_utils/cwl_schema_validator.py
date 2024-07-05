import logging

logger = logging.getLogger(__name__)

# List of unsupported requirements in CWL files
UNSUPPORTED_REQUIREMENTS = [
    'InlineJavascriptRequirement',
    'ResourceRequirement',
    'DockerRequirement',
]

VALID_CWL_VERSIONS = ['v1.0', 'v1.1']
VALID_CWL_CLASSES = ['CommandLineTool', 'Workflow']

class CWLSchemaValidator:
    """
    Validates the schema of CWL (Common Workflow Language) files.
    """
    def validate_cwl(self, cwl_data):
        """
        Validate the CWL data against the expected schema.

        Args:
            cwl_data (dict): The CWL data to validate.

        Returns:
            tuple: (bool, str) indicating whether the validation was successful and a message.
        """
        logging.info(f"Validating CWL data: {cwl_data}")
        try:
            # Check for the presence of 'cwlVersion'
            cwl_version = cwl_data.get('cwlVersion')
            if not cwl_version:
                raise ValueError("Missing 'cwlVersion' in CWL file")
            if cwl_version not in VALID_CWL_VERSIONS:
                raise ValueError(f"Unsupported CWL version: {cwl_version}")

            # Check for the presence of 'class'
            cwl_class = cwl_data.get('class')
            if not cwl_class:
                raise ValueError("Missing 'class' in CWL file")
            if cwl_class not in VALID_CWL_CLASSES:
                raise ValueError(f"Unsupported class: {cwl_class}")

            # Validate requirements if present
            requirements = cwl_data.get('requirements', [])
            if requirements:
                if not isinstance(requirements, list):
                    raise ValueError("Please define requirement in CWL as list")
                for item in requirements:
                    if item['class'] in UNSUPPORTED_REQUIREMENTS:
                        raise ValueError(f"Unsupported requirement: {item['class']}")

            # Validate hints if present
            hints = cwl_data.get('hints', [])
            if hints:
                if not isinstance(hints, list):
                    raise ValueError("Please define hints in CWL as list")
                for item in hints:
                    if item['class'] in UNSUPPORTED_REQUIREMENTS:
                        raise ValueError(f"Unsupported hint: {item['class']}")

            # Check for the presence of 'inputs'
            inputs = cwl_data.get('inputs')
            if not inputs:
                raise ValueError("Missing 'inputs' in CWL file")
            for input_name, input_data in inputs.items():
                if 'type' not in input_data:
                    raise ValueError(f"Missing 'type' for input '{input_name}'")

            # Check for the presence of 'outputs'
            outputs = cwl_data.get('outputs')
            if not outputs:
                raise ValueError("Missing 'outputs' in CWL file")
            for output_name, output_data in outputs.items():
                if 'type' not in output_data:
                    raise ValueError(f"Missing 'type' for output '{output_name}'")

            # If class is 'Workflow', ensure 'steps' are present and valid
            if cwl_class == "Workflow":
                steps = cwl_data.get('steps')
                if not steps:
                    raise ValueError("Missing 'steps' in CWL file")
                for step_name, step_data in steps.items():
                    if 'run' not in step_data:
                        raise ValueError(f"Missing 'run' for step '{step_name}'")
                    if 'in' not in step_data:
                        raise ValueError(f"Missing 'in' for step '{step_name}'")
                    if 'out' not in step_data:
                        raise ValueError(f"Missing 'out' for step '{step_name}'")

            # If class is 'CommandLineTool', validate command line tool specifics
            if cwl_class == "CommandLineTool":
                if 'baseCommand' not in cwl_data:
                    raise ValueError("Missing 'baseCommand' in CommandLineTool")
                if not isinstance(cwl_data.get('baseCommand'), (str, list)):
                    raise ValueError("'baseCommand' must be a string or list of strings")

            logging.info("CWL file is valid.")
            return True, "CWL file is valid."
        except Exception as e:
            # Log any exception that occurs during validation
            logging.error(f"Validation failed: {e}")
            return False, f"Validation failed: {e}"
