import os
import json
import logging
from ruamel.yaml import YAML
from django.core.exceptions import ObjectDoesNotExist
from ..models import Job, Step, Task, Environment

logger = logging.getLogger(__name__)

yaml = YAML()
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)

def parse_json_field(field):
    if isinstance(field, str):
        return json.loads(field)
    return field

def reconstruct_workflow_cwl(job, file_path):
    logger.info(f"Reconstructing workflow: {job.name}")

    workflow_detail = {
        "cwlVersion": job.cwl_version if job.cwl_version else "v1.0",
        "class": "Workflow",
        "inputs": {
            "input-file": {"type": "File"}  
        },
        "outputs": {
            "output-file": { 
                "type": "File",
                "outputSource": "psipass2/output"
            }
        },
        "steps": {},
        "requirements": parse_json_field(job.requirements)
    }

    steps = job.steps.all().order_by('ordering')
    for step in steps:
        task = step.task
        step_detail = _build_step_detail(step, task)
        workflow_detail["steps"][task.name] = step_detail

    # Save the CWL file
    try:
        with open(file_path, 'w') as file:
            yaml.dump(workflow_detail, file)
        logger.info(f"Workflow '{job.name}' saved as {file_path}")
    except Exception as e:
        logger.error(f"Failed to save workflow '{job.name}' as {file_path}: {str(e)}")


def _build_step_detail(step, task):
    # Construct step input-output relationship
    step_detail = {
        "run": f"{task.name}.cwl",
        "in": {},
        "out": [f"output_{i}" for i, _ in enumerate(task.out_glob.split(',')) if task.out_glob]
    }

    # Handling input bindings based on step order and input sources
    if step.ordering == 0:
        step_detail["in"]["input"] = "input-file"
    else:
        prev_step = step.job.steps.get(ordering=step.ordering - 1)
        prev_task_name = prev_step.task.name
        step_detail["in"]["input"] = f"{prev_task_name}/output"

    return step_detail

def _define_workflow_outputs(job, steps, workflow_detail):
    # Assume the last step's output is the workflow output
    last_step = steps.last()
    if last_step:
        last_task_name = last_step.task.name
        workflow_detail["outputs"]["output-wf"] = {
            "type": "File",
            "outputSource": f"{last_task_name}/output"
        }
