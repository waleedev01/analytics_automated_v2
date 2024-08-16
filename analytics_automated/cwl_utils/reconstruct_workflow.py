import os
import json
import logging
from ruamel.yaml import YAML
from ..models import Job, Step, Task

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
            "input_file": {"type": "File"}
        },
        "outputs": {},
        "steps": {},
        "requirements": parse_json_field(job.requirements) or []
    }

    # Add steps to the workflow
    steps = job.steps.all().order_by('ordering')
    for step in steps:
        task = step.task
        step_detail = _build_step_detail(step, task, steps)
        workflow_detail["steps"][task.name] = step_detail

    # Define the workflow's final outputs
    _define_workflow_outputs(job, steps, workflow_detail)

    # Save the CWL file
    try:
        with open(file_path, 'w') as file:
            yaml.dump(workflow_detail, file)
        logger.info(f"Workflow '{job.name}' saved as {file_path}")
    except Exception as e:
        logger.error(f"Failed to save workflow '{job.name}' as {file_path}: {str(e)}")


def _build_step_detail(step, task, steps):
    # Construct step input-output relationship
    step_detail = {
        "run": f"{task.name}.cwl",
        "in": {},
        "out": [f"output_{i}" for i, _ in enumerate(task.out_glob.split(',')) if task.out_glob]
    }

    # Set the inputs for the current step based on previous step's outputs
    if step.ordering == 0:
        step_detail["in"]["input_0"] = "input_file"
    else:
        prev_step = steps.get(ordering=step.ordering - 1)
        prev_task_name = prev_step.task.name
        prev_out_count = len(prev_step.task.out_glob.split(','))

        # Map previous task's outputs to current task's inputs
        for i in range(prev_out_count):
            step_detail["in"][f"input_{i}"] = f"{prev_task_name}/output_{i}"

    return step_detail

def _define_workflow_outputs(job, steps, workflow_detail):
    # Use the last step's outputs as the workflow outputs
    last_step = steps.last()
    if last_step:
        last_task_name = last_step.task.name
        last_out_count = len(last_step.task.out_glob.split(','))
        for i in range(last_out_count):
            workflow_detail["outputs"][f"output_file_{i}"] = {
                "type": "File",
                "outputSource": f"{last_task_name}/output_{i}"
            }
