import os
import json
import logging
from ruamel.yaml import YAML
from django.core.exceptions import ObjectDoesNotExist
from ..models import Task, Parameter, Environment

logger = logging.getLogger(__name__)

yaml = YAML()
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)

def parse_json_field(field):
    if isinstance(field, str):
        return json.loads(field)
    return field

def reconstruct_task_cwl(task, file_path):
    logger.info(f"Reconstructing task: {task.name}")
    
    task_detail = {
        "cwlVersion": "v1.0",
        "class": "CommandLineTool",
        "baseCommand": task.executable.split(),
        "inputs": {},  # Populate inputs appropriately
        "outputs": {},
        "requirements": parse_json_field(task.requirements),
        "hints": parse_json_field(task.hints),
        "successCodes": parse_json_field(task.success_codes),
        "temporaryFailCodes": parse_json_field(task.temporary_fail_codes),
        "permanentFailCodes": parse_json_field(task.permanent_fail_codes),
        "arguments": parse_json_field(task.arguments),
        "stdin": task.stdin,
        "stdout": task.stdout,
        "stderr": task.stderr,
        "doc": task.doc,
        "label": task.label,
        "shellQuote": task.shell_quote,
    }

    # Add input and output parameters
    _add_inputs(task, task_detail)
    _add_outputs(task, task_detail)

    # Add environment variables
    _add_environment(task, task_detail)

    # Save the CWL file
    try:
        with open(file_path, 'w') as file:
            yaml.dump(task_detail, file)
        logger.info(f"Task '{task.name}' saved as {file_path}")
    except Exception as e:
        logger.error(f"Failed to save task '{task.name}' as {file_path}: {str(e)}")


def _add_inputs(task, task_detail):
    parameters = task.parameters.all()
    for param in parameters:
        input_binding = {
            "position": param.spacing,
            "prefix": param.flag if not param.switchless else None
        }
        task_detail["inputs"][param.rest_alias] = {
            "type": "boolean" if param.bool_valued else "string",
            "inputBinding": input_binding
        }

def _add_outputs(task, task_detail):
    outputs = task.out_glob.split(',')
    if task.stdout:
        task_detail["outputs"]["output_stdout"] = {
            "type": "File",
            "outputBinding": {"glob": task.stdout}
        }
    for i, output in enumerate(outputs):
        if output.strip():
            task_detail["outputs"][f"output_{i}"] = {
                "type": "File",
                "outputBinding": {"glob": output}
            }




def _add_environment(task, task_detail):
    environments = task.environment.all()
    if environments.exists():
        task_detail["requirements"].append({
            "class": "EnvVarRequirement",
            "envDef": {env.env: env.value for env in environments}
        })
