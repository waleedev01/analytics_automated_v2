import os
import logging
from .reconstruct_task import reconstruct_task_cwl
from .reconstruct_workflow import reconstruct_workflow_cwl
from django.core.exceptions import ObjectDoesNotExist
from ..models import Job

logger = logging.getLogger(__name__)

def reconstruct_cwl_files(job_name, output_directory):
    """
    Reconstruct the CWL files for a given job (workflow) and save them to the specified output directory.

    Args:
        job_name (str): The name of the job (workflow) to reconstruct CWL files for.
        output_directory (str): The directory where the reconstructed CWL files will be saved.

    Raises:
        ValueError: If the specified job does not exist in the database.

    Returns:
        None
    """
    logger.info(f"Reconstructing CWL files for job: {job_name}")

    # Explicitly check if the provided name corresponds to a workflow (Job) and not a task
    try:
        job = Job.objects.get(name=job_name)
    except ObjectDoesNotExist:
        logger.error(f"Job '{job_name}' does not exist.")
        raise ValueError(f"Job '{job_name}' does not exist.")

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Reconstruct workflow
    workflow_file_path = os.path.join(output_directory, f"{job_name}.cwl")
    reconstruct_workflow_cwl(job, workflow_file_path)

    # Reconstruct each task within the workflow
    steps = job.steps.all().order_by('ordering')
    for step in steps:
        task = step.task
        task_file_path = os.path.join(output_directory, f"{task.name}.cwl")
        reconstruct_task_cwl(task, task_file_path)

    logger.info(f"Reconstruction completed for job: {job_name}")

