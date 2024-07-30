import logging
import json
import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.conf import settings
from ..models import Task, Parameter, Environment

logger = logging.getLogger(__name__)

def load_format_mapping():
    """
    Load format URI mappings from a JSON file.
    """
    format_map_path = os.path.join(settings.BASE_DIR, 'analytics_automated', 'cwl_utils', 'format_uri_mapping.json')
    try:
        with open(format_map_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Format mapping file not found: {format_map_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to parse format mapping file: {format_map_path}")
        return {}

FORMAT_MAP = load_format_mapping()

def safe_json_loads(data):
    """
    Safely load JSON data from a string.
    """
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {data}")
            return data
    return data

def get_task_details(task):
    """
    Reconstructs the CWL CommandLineTool from the database task object.
    """
    logger.debug(f"Starting to process task: {task.name}")
    
    task_detail = {
        "cwlVersion": "v1.0",
        "class": "CommandLineTool",
        "baseCommand": task.executable.split()
    }

    # Process inputs
    task_detail["inputs"] = reconstruct_inputs(task)

    # Process outputs
    task_detail["outputs"] = reconstruct_outputs(task)

    # Process stdout
    if task.stdout_glob:
        input_name = next(iter(task_detail["inputs"]))
        task_detail["stdout"] = f"$(inputs.{input_name}.basename){task.stdout_glob}"

    # Process optional attributes and requirements
    if task.requirements:
        task_detail["requirements"] = safe_json_loads(task.requirements)
    
    if task.arguments:
        task_detail["arguments"] = safe_json_loads(task.arguments)
    
    if task.hints:
        task_detail["hints"] = safe_json_loads(task.hints)

    if task.stdin:
        task_detail["stdin"] = task.stdin

    if task.stdout:
        task_detail["stdout"] = task.stdout

    if task.stderr:
        task_detail["stderr"] = task.stderr

    logger.debug(f"Final task detail: {task_detail}")
    return task_detail

def reconstruct_inputs(task):
    """
    Reconstruct inputs for a CommandLineTool.
    """
    inputs = {}
    params = task.parameters.all()
    
    for param in params:
        input_name = param.rest_alias
        input_detail = {
            "type": "File",
            "inputBinding": {"position": 1}
        }
        
        if task.in_glob:
            format_uri = next((k for k, v in FORMAT_MAP.items() if v == f".{task.in_glob.strip('.')}" or v == task.in_glob), None)
            if format_uri:
                input_detail["format"] = format_uri
        
        inputs[input_name] = input_detail
    
    return inputs

def reconstruct_outputs(task):
    """
    Reconstruct outputs for a CommandLineTool.
    """
    outputs = {}
    if task.out_glob:
        output_globs = task.out_glob.split(',')
        for i, glob in enumerate(output_globs):
            output_name = f"output_{task.name.lower()}" if i == 0 else f"output_{task.name.lower()}_{i+1}"
            outputs[output_name] = {
                "type": "File",
                "outputBinding": {"glob": f"*.{glob.strip('.')}"}
            }
    return outputs

@transaction.atomic
def reconstruct_task(task_name):
    """
    Reconstruct a CommandLineTool task from its database entry.
    """
    logger.info(f"Starting task reconstruction for: {task_name}")
    try:
        task = Task.objects.get(name=task_name)
    except ObjectDoesNotExist:
        logger.error(f"Task '{task_name}' does not exist.")
        return None

    try:
        task_detail = get_task_details(task)
        return task_detail
    except Exception as e:
        logger.error(f"Error reconstructing task: {str(e)}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    task = reconstruct_task("example_task_name")
    if task:
        print(json.dumps(task, indent=2))
    else:
        print("Failed to reconstruct task")