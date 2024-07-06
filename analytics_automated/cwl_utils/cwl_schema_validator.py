import logging

logger = logging.getLogger(__name__)

# List of unsupported requirements in CWL files
UNSUPPORTED_REQUIREMENTS = [
    'InlineJavascriptRequirement',
    'ResourceRequirement',
    'DockerRequirement',
]

VALID_CWL_VERSIONS = ['v1.0', 'v1.1','v1.2']
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
        errors = []
        try:
            # Check for the presence of 'cwlVersion'
            cwl_version = cwl_data.get('cwlVersion')
            if not cwl_version:
                errors.append("Missing 'cwlVersion' in CWL file")
            elif cwl_version not in VALID_CWL_VERSIONS:
                errors.append(f"Unsupported CWL version: {cwl_version}")

            # Check for the presence of 'class'
            cwl_class = cwl_data.get('class')
            if not cwl_class:
                errors.append("Missing 'class' in CWL file")
            elif cwl_class not in VALID_CWL_CLASSES:
                errors.append(f"Unsupported class: {cwl_class}")

            # Validate requirements if present
            requirements = cwl_data.get('requirements', [])
            if requirements:
                if not isinstance(requirements, list):
                    errors.append("Please define requirement in CWL as list")
                else:
                    for item in requirements:
                        if item.get('class') in UNSUPPORTED_REQUIREMENTS:
                            errors.append(f"Unsupported requirement: {item['class']}")

            # Validate hints if present
            hints = cwl_data.get('hints', [])
            if hints:
                if not isinstance(hints, list):
                    errors.append("Please define hints in CWL as list")
                else:
                    for item in hints:
                        if item.get('class') in UNSUPPORTED_REQUIREMENTS:
                            errors.append(f"Unsupported hint: {item['class']}")

            # Check for the presence of 'inputs'
            inputs = cwl_data.get('inputs')
            if not inputs:
                errors.append("Missing 'inputs' in CWL file")
            else:
                for input_name, input_data in inputs.items():
                    if 'type' not in input_data:
                        errors.append(f"Missing 'type' for input '{input_name}'")

            # Check for the presence of 'outputs'
            outputs = cwl_data.get('outputs')
            if not outputs:
                errors.append("Missing 'outputs' in CWL file")
            else:
                for output_name, output_data in outputs.items():
                    if 'type' not in output_data:
                        errors.append(f"Missing 'type' for output '{output_name}'")

            # If class is 'Workflow', ensure 'steps' are present and valid
            if cwl_class == "Workflow":
                steps = cwl_data.get('steps')
                if not steps:
                    errors.append("Missing 'steps' in CWL file")
                else:
                    for step_name, step_data in steps.items():
                        if 'run' not in step_data:
                            errors.append(f"Missing 'run' for step '{step_name}'")
                        if 'in' not in step_data:
                            errors.append(f"Missing 'in' for step '{step_name}'")
                        if 'out' not in step_data:
                            errors.append(f"Missing 'out' for step '{step_name}'")

            # If class is 'CommandLineTool', validate command line tool specifics
            if cwl_class == "CommandLineTool":
                if 'baseCommand' not in cwl_data:
                    errors.append("Missing 'baseCommand' in CommandLineTool")
                elif not isinstance(cwl_data.get('baseCommand'), (str, list)):
                    errors.append("'baseCommand' must be a string or list of strings")

            if errors:
                raise ValueError("; ".join(errors))

            logging.info("CWL file is valid.")
            return True, "CWL file is valid."
        except Exception as e:
            # Log any exception that occurs during validation
            logging.error(f"Validation failed: {e}")
            return False, f"Validation failed: {e}"
