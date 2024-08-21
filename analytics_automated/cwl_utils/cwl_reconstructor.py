import os
import logging
from ruamel.yaml import YAML
from .models import Job, Step, Task, Environment, Parameter

logger = logging.getLogger(__name__)

# Utility functions for YAML handling
def represent_str(self, data):
    """
    Custom YAML representation for strings.

    Args:
        data (str): The string data to be represented.

    Returns:
        YAML representer: The YAML representer for the string.
    """
    if '\n' in data:
        return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return self.represent_scalar('tag:yaml.org,2002:str', data, style='')

def represent_list(self, data):
    """
    Custom YAML representation for lists.

    Args:
        data (list): The list data to be represented.

    Returns:
        YAML representer: The YAML representer for the list.
    """
    if len(data) == 1 and isinstance(data[0], str):
        return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
    return self.represent_sequence('tag:yaml.org,2002:seq', data)

yaml = YAML()
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096
yaml.representer.add_representer(str, represent_str)
yaml.representer.add_representer(list, represent_list)

def save_cwl_file(cwl_content, file_path):
    """
    Save the CWL content to a file.

    Args:
        cwl_content (dict): The CWL content to be saved.
        file_path (str): The path to the file where the content will be saved.

    Returns:
        None
    """
    logger.debug(f"Saving CWL file: {file_path}")
    try:
        with open(file_path, 'w') as file:
            yaml.dump(cwl_content, file)
    except Exception as e:
        logger.error(f"Failed to save CWL file {file_path}: {str(e)}")

def reconstruct_cwl(job_name, output_directory):
    """
    Reconstruct CWL files from the database based on a job name.

    Args:
        job_name (str): The name of the job for which CWL files will be reconstructed.
        output_directory (str): The directory where the reconstructed CWL files will be saved.

    Returns:
        None
    """
    try:
        job = Job.objects.get(name=job_name)
        logger.info(f"Reconstructing CWL for job: {job_name}")
        
        # Create output directory
        os.makedirs(output_directory, exist_ok=True)

        # Reconstruct each task
        steps = job.steps.all().order_by('ordering')
        for step in steps:
            task = step.task
            task_cwl = reconstruct_task_cwl(task)
            task_file_path = os.path.join(output_directory, f"{task.name}.cwl")
            save_cwl_file(task_cwl, task_file_path)

        # Reconstruct workflow
        workflow_cwl = reconstruct_workflow_cwl(job)
        workflow_file_path = os.path.join(output_directory, f"{job_name}_workflow.cwl")
        save_cwl_file(workflow_cwl, workflow_file_path)

    except Exception as e:
        logger.error(f"Failed to reconstruct CWL for job '{job_name}': {str(e)}")

def reconstruct_task_cwl(task):
    """
    Reconstruct a CommandLineTool CWL for a given task.

    Args:
        task (Task): The task object for which the CWL will be reconstructed.

    Returns:
        dict: The reconstructed CWL content as a dictionary.
    """
    logger.debug(f"Reconstructing task: {task.name}")
    task_detail = {
        "cwlVersion": "v1.0",
        "class": "CommandLineTool",
        "baseCommand": task.executable.split(),
        "inputs": reconstruct_task_inputs(task),
        "outputs": reconstruct_task_outputs(task),
        "requirements": task.requirements or [],
        "hints": task.hints or [],
        "arguments": task.arguments or [],
        "stdin": task.stdin,
        "stdout": task.stdout,
        "stderr": task.stderr,
    }

    return task_detail

def reconstruct_task_inputs(task):
    """
    Reconstruct inputs for a task.

    Args:
        task (Task): The task object whose inputs will be reconstructed.

    Returns:
        dict: A dictionary representing the reconstructed inputs.
    """
    inputs = {}
    for param in task.parameters.all():
        inputs[param.rest_alias] = {
            "type": "File" if param.bool_valued else "string",
            "inputBinding": {"prefix": param.flag} if param.flag else {}
        }
    return inputs

def reconstruct_task_outputs(task):
    """
    Reconstruct outputs for a task.

    Args:
        task (Task): The task object whose outputs will be reconstructed.

    Returns:
        dict: A dictionary representing the reconstructed outputs.
    """
    outputs = {}
    if task.out_glob:
        outputs["output"] = {
            "type": "File",
            "outputBinding": {"glob": task.out_glob}
        }
    return outputs

def reconstruct_workflow_cwl(job):
    """
    Reconstruct outputs for a task.

    Args:
        task (Task): The task object whose outputs will be reconstructed.

    Returns:
        dict: A dictionary representing the reconstructed outputs.
    """
    logger.debug(f"Reconstructing workflow: {job.name}")
    steps = job.steps.all().order_by('ordering')

    workflow_steps = {}
    for step in steps:
        task = step.task
        step_detail = {
            "run": f"{task.name}.cwl",
            "in": {},
            "out": [f"output"]
        }

        # Map inputs from previous steps
        if step.ordering > 0:
            prev_step = steps[step.ordering - 1].task
            step_detail["in"]["input"] = f"{prev_step.name}/output"

        workflow_steps[task.name] = step_detail

    workflow_cwl = {
        "cwlVersion": job.cwl_version or "v1.0",
        "class": "Workflow",
        "inputs": {"input-file": {"type": "File"}},
        "outputs": {
            "output-file": {
                "type": "File",
                "outputSource": f"{steps.last().task.name}/output"
            }
        },
        "steps": workflow_steps
    }

    return workflow_cwl
