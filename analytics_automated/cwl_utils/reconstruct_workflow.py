import logging
import json
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ..models import Job, Step, Task, Parameter

logger = logging.getLogger(__name__)

VALID_CWL_VERSIONS = ['v1.0', 'v1.1', 'v1.2', 'v1.3']

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

def get_step_sources(job):
    """
    Extract step sources for a job from the database.
    """
    steps = job.steps.all().order_by('ordering')
    step_source = {}
    for step in steps:
        sources = set()
        for param in step.task.parameters.all():
            if param.rest_alias and '_' in param.rest_alias:
                source_step = param.rest_alias.split('_')[0]
                if source_step.isdigit():
                    sources.add(int(source_step))
        step_source[step.task.name] = sources
    return step_source

def set_step_order(step_source):
    """
    Determine the order of steps in the workflow based on their dependencies.
    """
    order_mapping = {}
    for step_name, source_list in step_source.items():
        if len(source_list) == 0:
            order_mapping[step_name] = 0
        else:
            order = max([order_mapping.get(source, 0) for source in source_list]) + 1
            order_mapping[step_name] = order
    return order_mapping

def get_workflow_details(job):
    """
    Construct the details of a workflow from its database representation.
    """
    logger.debug(f"Starting to process workflow for job: {job.name}")
    steps = job.steps.all().order_by('ordering')
    workflow_steps = {}

    workflow_input = {
        "input-file": {"type": "File"}
    }

    for i, step in enumerate(steps):
        task = step.task
        step_name = task.name
        step_detail = {
            "run": f"{step_name}.cwl",
            "in": {},
            "out": []
        }

        # Process inputs
        if i == 0:
            step_detail["in"]["input"] = "input-file"
        else:
            step_detail["in"]["input"] = f"{steps[i-1].task.name}/output"

        # Process outputs
        if task.out_glob:
            step_detail["out"] = [f"output"]

        workflow_steps[step_name] = step_detail

    last_step = steps.last()
    workflow_output = {
        "output-file": {
            "type": "File",
            "outputSource": f"{last_step.task.name}/output"
        }
    }

    workflow_detail = {
        "cwlVersion": job.cwl_version if job.cwl_version in VALID_CWL_VERSIONS else "v1.0",
        "class": "Workflow",
        "inputs": workflow_input,
        "outputs": workflow_output,
        "steps": workflow_steps,
    }

    if job.requirements:
        workflow_detail["requirements"] = safe_json_loads(job.requirements)

    logger.debug(f"Final workflow detail: {workflow_detail}")
    return workflow_detail

@transaction.atomic
def reconstruct_workflow(job_name):
    """
    Reconstruct a workflow from its database entry.
    """
    logger.info(f"Starting workflow reconstruction for job: {job_name}")
    try:
        job = Job.objects.get(name=job_name)
    except ObjectDoesNotExist:
        logger.error(f"Job '{job_name}' does not exist.")
        return None

    try:
        workflow_detail = get_workflow_details(job)
        return workflow_detail
    except Exception as e:
        logger.error(f"Error reconstructing workflow: {str(e)}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    workflow = reconstruct_workflow("example_job_name")
    if workflow:
        print(json.dumps(workflow, indent=2))
    else:
        print("Failed to reconstruct workflow")