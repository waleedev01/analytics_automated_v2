import logging

logger = logging.getLogger(__name__)
UNSUPPORTED_REQUIREMENTS = [
    'InlineJavascriptRequirement',
    'ResourceRequirement',
    'DockerRequirement',
]

class CWLSchemaValidator:
    def validate_cwl(self, cwl_data):
        try:
            if not cwl_data.get('cwlVersion'):
                raise ValueError("Missing 'cwlVersion' in CWL file")

            if not cwl_data.get('class'):
                raise ValueError("Missing 'class' in CWL file")

            requirements = cwl_data.get('requirements', [])
            if requirements:
                if not isinstance(requirements, list):
                    raise ValueError("Please define requirement in CWL as list")
                for item in requirements:
                    if item['class'] in UNSUPPORTED_REQUIREMENTS:
                        raise ValueError(f"Unsupported requirement: {item['class']}")

            return True, "CWL file is valid."
        except Exception as e:
            logging.error(f"Validation failed: {str(e)}")
            return False, f"Validation failed: {str(e)}"
