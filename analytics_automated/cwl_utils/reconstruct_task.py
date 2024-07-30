import logging
import json
import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.conf import settings
from ..models import Task, Parameter, Environment

logger = logging.getLogger(__name__)

def load_format_mapping():
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
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {data}")
            return data
    return data

def get_task_details(task):
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

    # Process optional attributes plus requirements
    # task_detail.update(reconstruct_additional_attributes(task))

    logger.debug(f"Final task detail: {task_detail}")
    return task_detail

def reconstruct_inputs(task):
    inputs = {}
    params = task.parameters.all()
    
    if params:
        for param in params:
            input_name = param.rest_alias or f"input_{task.name}_file"
            input_detail = {
                "type": "File",
                "inputBinding": {"position": 1}
            }
            
            if task.in_glob:
                format_uri = next((k for k, v in FORMAT_MAP.items() if v == f".{task.in_glob.strip('.')}" or v == task.in_glob), None)
                if format_uri:
                    input_detail["format"] = format_uri
            
            inputs[input_name] = input_detail
    else:
        # If no parameters, create a default input
        input_name = f"input_{task.name}_file"
        inputs[input_name] = {
            "type": "File",
            "inputBinding": {"position": 1}
        }
        if task.in_glob:
            format_uri = next((k for k, v in FORMAT_MAP.items() if v == f".{task.in_glob.strip('.')}" or v == task.in_glob), None)
            if format_uri:
                inputs[input_name]["format"] = format_uri

    return inputs

def reconstruct_outputs(task):
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

# def reconstruct_additional_attributes(task):
#     attributes = {}

#     # Process environments
#     environments = task.environment_set.all()
#     if environments:
#         attributes["requirements"] = [{
#             "class": "EnvVarRequirement",
#             "envDef": {env.env: env.value for env in environments}
#         }]

#     # Process stdin, stdout, stderr
#     if task.stdin:
#         attributes["stdin"] = task.stdin
#     if task.stderr:
#         attributes["stderr"] = task.stderr

    # return attributes

@transaction.atomic
def reconstruct_task(task_name):
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