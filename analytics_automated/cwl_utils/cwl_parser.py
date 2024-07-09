import yaml
import logging
from .cwl_schema_validator import CWLSchemaValidator
from .cwl_workflow_handler import parse_cwl_workflow
from .cwl_clt_handler import parse_cwl_clt, save_task_to_db

logger = logging.getLogger(__name__)

def read_cwl_file(cwl_path, filename, messages):
    """
    Reads and processes a CWL file, validating its schema and parsing it as either a Workflow or CommandLineTool.
    
    Args:
        cwl_path (str): The path to the CWL file.
        filename (str): The name of the file being processed.
        messages (list): A list to store messages about the processing results.
    
    Returns:
        The result of the CWL parsing, or None if an error occurred.
    """
    logging.info(f"Reading CWL file: {cwl_path}")
    try:
        # Load the CWL file
        with open(cwl_path, 'r') as cwl_file:
            cwl_data = yaml.safe_load(cwl_file)

        # Validate the CWL schema
        validator = CWLSchemaValidator()
        is_valid, message = validator.validate_cwl(cwl_data)

        if not is_valid:
            logger.error(f"Validation Failed: {message}")
            messages.append(f"Validation Failed: {message}")
            return None

        # Determine the class of the CWL (Workflow or CommandLineTool)
        cwl_class = cwl_data.get("class")

        if cwl_class == "Workflow":
            logging.info(f"Parsing workflow: {filename}")
            return parse_cwl_workflow(cwl_data, filename, messages)
        elif cwl_class == "CommandLineTool":
            logging.info(f"Parsing CommandLineTool: {filename}")
            task_data = parse_cwl_clt(cwl_data, filename)
            return save_task_to_db(task_data, messages)
        else:
            # Handle unknown CWL class
            error_message = f"Unknown CWL class for file {cwl_path}"
            logger.error(error_message)
            messages.append(error_message)
            return None
    except Exception as e:
        # Log any exception that occurs during the processing
        error_message = f"Error reading CWL file {cwl_path}: {e}"
        logger.error(error_message)
        messages.append(error_message)
        return None
