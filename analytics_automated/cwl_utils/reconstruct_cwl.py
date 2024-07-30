import os
import logging
from django.core.exceptions import ObjectDoesNotExist
from ruamel.yaml import YAML
from ..models import Job, Step
from .reconstruct_task import get_task_details
from .reconstruct_workflow import get_workflow_details

logger = logging.getLogger(__name__)

def represent_str(self, data):
    if '\n' in data:
        return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return self.represent_scalar('tag:yaml.org,2002:str', data, style='')

def represent_list(self, data):
    if len(data) == 1 and isinstance(data[0], str):
        return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
    return self.represent_sequence('tag:yaml.org,2002:seq', data)

def save_cwl_file(cwl_content, file_path):
    logger.debug(f"Saving CWL file: {file_path}")
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096

    yaml.representer.add_representer(str, represent_str)
    yaml.representer.add_representer(list, represent_list)

    try:
        with open(file_path, 'w') as file:
            yaml.dump(cwl_content, file)

        with open(file_path, 'r') as file:
            content = file.readlines()
        
        new_content = []
        for line in content:
            new_content.append(line)
            if line.strip() == "class: Workflow":
                new_content.append("\n")
        
        with open(file_path, 'w') as file:
            file.writelines(new_content)

        logger.debug(f"Successfully saved CWL file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save CWL file {file_path}: {str(e)}")

def reconstruct_cwl_files(job_name, output_directory):
    logger.info(f"Starting CWL reconstruction for job: {job_name}")
    try:
        job = Job.objects.get(name=job_name)
    except ObjectDoesNotExist:
        logger.error(f"Job '{job_name}' does not exist.")
        return
    
    os.makedirs(output_directory, exist_ok=True)
    logger.debug(f"Created output directory: {output_directory}")

    workflow_detail = get_workflow_details(job)
    workflow_file_path = os.path.join(output_directory, f"{job_name}.cwl")
    save_cwl_file(workflow_detail, workflow_file_path)

    steps = Step.objects.filter(job=job)
    for step in steps:
        logger.debug(f"Processing step {step.ordering} for task: {step.task.name}")
        task = step.task
        task_detail = get_task_details(task)
        task_file_path = os.path.join(output_directory, f"{task.name}.cwl")
        save_cwl_file(task_detail, task_file_path)

    logger.info(f"Successfully reconstructed CWL files for job '{job_name}' in '{output_directory}'")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    reconstruct_cwl_files("example_job_name", "./output_directory")