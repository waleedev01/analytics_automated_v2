import logging
import os
import re
from cwltool.load_tool import fetch_document, resolve_and_validate_document
from cwltool.context import LoadingContext

logger = logging.getLogger(__name__)

# List of supported requirements in CWL files
SUPPORTED_REQUIREMENTS = [
    'ShellCommandRequirement',
    'EnvVarRequirement',
    'InitialWorkDirRequirement',
    'SoftwareRequirement',
    'InlineJavascriptRequirement'
]

VALID_CWL_VERSIONS = ['v1.0', 'v1.1', 'v1.2']
VALID_CWL_CLASSES = ['CommandLineTool', 'Workflow']

class CWLSchemaValidator:
    """
    Validates the schema of CWL (Common Workflow Language) files.
    """
    def __init__(self):
        self.loading_context = LoadingContext()

    def validate_cwl(self, cwl_data):
        """
        Validate the CWL file or data against the expected schema.

        Args:
            cwl_data (str or dict): The path to the CWL file or the CWL data to validate.

        Returns:
            tuple: (bool, str) indicating whether the validation was successful and a message.
        """
        workflowobj = None
        if isinstance(cwl_data, str) and os.path.exists(cwl_data):
            # Validate from a CWL file path
            try:
                self.loading_context, workflowobj, uri = fetch_document(cwl_data, self.loading_context)
                self.loading_context, uri = resolve_and_validate_document(self.loading_context, workflowobj, uri, preprocess_only=False)
                logging.info("CWL file is valid.")
                return True, "CWL file is valid."
            except Exception as e:
                logging.error(f"Validation failed: {e}")
                return False, f"Validation failed: {e}"

        return self.manual_validation(cwl_data if isinstance(cwl_data, dict) else {})

    def manual_validation(self, cwl_data):
        """
        Perform manual validation of CWL data.

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
                    errors.append("Please define requirements in CWL as list")
                else:
                    for item in requirements:
                        if not isinstance(item, dict):
                            errors.append(f"Unsupported requirement format: {item}")
                        elif item.get('class') not in SUPPORTED_REQUIREMENTS:
                            errors.append(f"Unsupported requirement: {item.get('class')}")
                        elif cwl_class == "CommandLineTool" and item.get('class') == "InlineJavascriptRequirement":
                            errors.append(f"Unsupported requirement: {item.get('class')} for CommandLineTool")

            # Validate hints if present
            hints = cwl_data.get('hints', [])
            if hints:
                if not isinstance(hints, list):
                    errors.append("Please define hints in CWL as list")
                else:
                    for item in hints:
                        if not isinstance(item, dict):
                            errors.append(f"Unsupported hint format: {item}")
                        elif item.get('class') not in SUPPORTED_REQUIREMENTS:
                            errors.append(f"Unsupported hint: {item.get('class')}")

            # Check for the presence of 'inputs'
            inputs = cwl_data.get('inputs')
            if not inputs:
                errors.append("Missing 'inputs' in CWL file")
            elif not isinstance(inputs, dict):
                errors.append("Please define inputs in CWL as dictionary")

            # Check for the presence of 'outputs'
            outputs = cwl_data.get('outputs')
            if not outputs:
                errors.append("Missing 'outputs' in CWL file")
            elif not isinstance(outputs, dict):
                errors.append("Please define outputs in CWL as dictionary")

            # If class is 'Workflow', ensure 'steps' are present and valid
            if cwl_class == "Workflow":
                steps = cwl_data.get('steps')
                if not steps:
                    errors.append("Missing 'steps' in CWL file")
                elif not isinstance(steps, dict):
                    errors.append("Please define steps in CWL as dictionary")
                else:
                    for step_name, step_data in steps.items():
                        if 'run' not in step_data:
                            errors.append(f"Missing 'run' for step '{step_name}'")
                        if 'in' not in step_data:
                            errors.append(f"Missing 'in' for step '{step_name}'")
                        if 'out' not in step_data:
                            errors.append(f"Missing 'out' for step '{step_name}'")
                        if 'when' in step_data:
                            if cwl_version not in ['v1.2']:
                                errors.append(f"'when' is only supported in CWL v1.2 and above")
                            
                            when_condition = step_data.get('when')
                            if not when_condition.startswith('$(inputs.exit_code'):
                                errors.append(f"Invalid 'when' condition for step '{step_name}'. Currently, we only support 'exit_code' condition with format '$(inputs.exit_code ...)'")
                            
                            pattern = r'==|!=|>=|<=|>|<'
                            exit_code = re.split(pattern, when_condition)[-1]
                            exit_code = exit_code.replace(')', '')
                            try:
                                int(exit_code)
                            except ValueError:
                                errors.append(f"Invalid 'exit_code' value in 'when' condition for step '{step_name}'")

            # If class is 'CommandLineTool', validate command line tool specifics
            if cwl_class == "CommandLineTool":
                if 'baseCommand' not in cwl_data and not cwl_data.get('arguments', []):
                    errors.append("Missing 'baseCommand' in CommandLineTool")
                elif 'baseCommand' in cwl_data and not isinstance(cwl_data.get('baseCommand'), (str, list)):
                    errors.append("'baseCommand' must be a string or list of strings")

                # Validate optional fields if present
                if 'arguments' in cwl_data and not isinstance(cwl_data.get('arguments'), list):
                    errors.append("'arguments' must be a list")
                if 'stdin' in cwl_data and not isinstance(cwl_data.get('stdin'), str):
                    errors.append("'stdin' must be a string")
                if 'stdout' in cwl_data and not isinstance(cwl_data.get('stdout'), str):
                    errors.append("'stdout' must be a string")
                if 'stderr' in cwl_data and not isinstance(cwl_data.get('stderr'), str):
                    errors.append("'stderr' must be a string")
                
                requirements = cwl_data.get('requirements', [])
                if requirements:
                    if not isinstance(requirements, list):
                        errors.append("Please define requirements in CWL as list")
                    else:
                        for item in requirements:
                            if not isinstance(item, dict):
                                errors.append(f"Unsupported requirement format: {item}")
                            elif item.get('class') == "InlineJavascriptRequirement":
                                errors.append(f"Unsupported requirement: {item['class']} for CommandLineTool")

            if errors:
                raise ValueError("; ".join(errors))

            logging.info("CWL file is valid.")
            return True, "CWL file is valid."
        except Exception as e:
            # Log any exception that occurs during validation
            logging.error(f"Validation failed: {e}")
            return False, f"Validation failed: {e}"
