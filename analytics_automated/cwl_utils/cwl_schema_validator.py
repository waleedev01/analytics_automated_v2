import logging

logger = logging.getLogger(__name__)

# List of unsupported requirements in CWL files
UNSUPPORTED_REQUIREMENTS = [
    'InlineJavascriptRequirement',
    'ResourceRequirement',
    'DockerRequirement',
]

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
            if not cwl_data.get('cwlVersion'):
                raise ValueError("Missing 'cwlVersion' in CWL file")

            # Check for the presence of 'class'
            if not cwl_data.get('class'):
                raise ValueError("Missing 'class' in CWL file")

            # Validate requirements if present
            requirements = cwl_data.get('requirements', [])
            if requirements:
                if not isinstance(requirements, list):
                    raise ValueError("Please define requirement in CWL as list")
                for item in requirements:
                    if item['class'] in UNSUPPORTED_REQUIREMENTS:
                        raise ValueError(f"Unsupported requirement: {item['class']}")
            
            # Check for the presence of 'inputs'
            if not cwl_data.get('inputs'):
                raise ValueError("Missing 'inputs' in CWL file")
            
            # Check for the presence of 'outputs'
            if not cwl_data.get('outputs'):
                raise ValueError("Missing 'outputs' in CWL file")
            
            # If class is 'Workflow', ensure 'steps' are present
            if cwl_data.get('class') == "Workflow":
                if not cwl_data.get('steps'):
                    raise ValueError("Missing 'steps' in CWL file")

            logging.info("CWL file is valid.")
            return True, "CWL file is valid."
        except Exception as e:
            # Log any exception that occurs during validation
            logging.error(f"Validation failed: {e}")
            return False, f"Validation failed: {e}"
