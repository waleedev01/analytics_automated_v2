import yaml
import logging
from .cwl_schema_validator import CWLSchemaValidator
from .cwl_workflow_handler import parse_cwl_workflow
from .cwl_clt_handler import parse_cwl_clt, save_task_to_db

logger = logging.getLogger(__name__)

def read_cwl_file(cwl_path, filename, messages):
    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)

    validator = CWLSchemaValidator()
    is_valid, message = validator.validate_cwl(cwl_data)

    if not is_valid:
        logger.error(f"Validation Failed: {message}")
        messages.append(f"Validation Failed: {message}")
        return None

    cwl_class = cwl_data.get("class")

    if cwl_class == "Workflow":
        return parse_cwl_workflow(cwl_data, filename, messages)
    elif cwl_class == "CommandLineTool":
        task_data = parse_cwl_clt(cwl_data, filename)
        return save_task_to_db(task_data, messages)
    else:
        error_message = f"Unknown CWL class for file {cwl_path}"
        logger.error(error_message)
        messages.append(error_message)
        return None
