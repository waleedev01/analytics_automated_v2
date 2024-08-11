import os
import json
import logging
from ruamel.yaml import YAML
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
        "inputs": {},
        "outputs": {},
        "requirements": parse_json_field(task.requirements) or [],
    }

    # Conditionally add non-empty fields
    if task.hints:
        task_detail["hints"] = parse_json_field(task.hints)

    if task.success_codes:
        task_detail["successCodes"] = parse_json_field(task.success_codes)

    if task.temporary_fail_codes:
        task_detail["temporaryFailCodes"] = parse_json_field(task.temporary_fail_codes)

    if task.permanent_fail_codes:
        task_detail["permanentFailCodes"] = parse_json_field(task.permanent_fail_codes)

    if task.arguments:
        task_detail["arguments"] = parse_json_field(task.arguments)

    if task.stdin:
        task_detail["stdin"] = task.stdin

    if task.stdout:
        task_detail["stdout"] = task.stdout

    if task.stderr:
        task_detail["stderr"] = task.stderr

    if task.doc:
        task_detail["doc"] = task.doc

    if task.label:
        task_detail["label"] = task.label

    task_detail["shellQuote"] = task.shell_quote

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
    # Define inputs based on task parameters
    in_globs = task.in_glob.split(',')
    for i, glob in enumerate(in_globs):
        if glob.strip():  # Skip empty globs
            task_detail["inputs"][f"input_{i}"] = {
                "type": "File",
                "inputBinding": {"position": i + 1}
            }

def _add_outputs(task, task_detail):
    # Define outputs based on task outputs
    out_globs = task.out_glob.split(',')
    if task.stdout:
        task_detail["outputs"]["stdout"] = {
            "type": "File",
            "outputBinding": {"glob": task.stdout}
        }
    for i, output in enumerate(out_globs):
        if output.strip():  # Skip empty outputs
            task_detail["outputs"][f"output_{i}"] = {
                "type": "File",
                "outputBinding": {"glob": output}
            }

def _add_environment(task, task_detail):
    # Add environment variables
    environments = task.environment.all()
    if environments.exists():
        task_detail["requirements"].append({
            "class": "EnvVarRequirement",
            "envDef": {env.env: env.value for env in environments}
        })
