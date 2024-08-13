from celery import Celery, shared_task
import os
import subprocess
import json
import logging
from analytics_automated.tasks import task_job_runner

# Configure Celery
app = Celery('tasks', broker='pyamqp://guest@localhost//')

# Directory containing the .cwl files
WORKFLOW_DIR = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen-cwl/'

# Helper function to run cwltool
def run_cwltool(cwl_file, input_file):
    try:
        result = subprocess.run(
            ['cwltool', cwl_file, input_file],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running cwltool: {e}")
        return None

# Task to execute a CWL file and return the result
@shared_task
def run_cwl_task(cwl_file, input_file):
    output = run_cwltool(cwl_file, input_file)
    return output

# Function to run all CWL files and compare results
def run_and_compare_all_cwls(input_file):
    cwl_files = [f for f in os.listdir(WORKFLOW_DIR) if f.endswith('.cwl')]
    tasks = []
    
    # Start tasks for each CWL file
    for cwl_file in cwl_files:
        task = run_cwl_task.delay(os.path.join(WORKFLOW_DIR, cwl_file), input_file)
        tasks.append(task)

    # Collect results
    results = [task.get() for task in tasks]

    # Compare results
    first_result = results[0]
    for result in results[1:]:
        if result != first_result:
            logging.info("Results are different!")
            return False

    logging.info("All results are the same.")
    return True

def run_cwl_files_and_compare_results(directory_path):
    """
    Run all .cwl files in the given directory and compare their results.

    :param directory_path: The path to the directory containing .cwl files.
    :return: A boolean indicating if all results are identical.
    """
    # List to store the results
    results = []

    # Find all .cwl files in the directory
    cwl_files = [f for f in os.listdir(directory_path) if f.endswith('.cwl')]

    # Run each .cwl file using task_job_runner
    for cwl_file in cwl_files:
        file_path = os.path.join(directory_path, cwl_file)
        
        # Assuming you have a way to create a job name or ID from the file path
        job_id = create_job_id_from_file(file_path)  # Implement this function as needed
        
        # Trigger the task (assuming task_job_runner takes a job name or ID)
        result = task_job_runner.apply_async(args=[job_id])

        # Wait for the task to complete (or use an appropriate method to get the result)
        result.get(timeout=3600)  # Adjust timeout as needed

        # Fetch result from your result storage (implement get_result_by_job_id as needed)
        job_result = get_result_by_job_id(job_id)  # Implement this function as needed
        results.append(job_result)

    # Compare all results
    if len(set(results)) == 1:
        print("All results are identical.")
        return True
    else:
        print("Results differ.")
        return False

def create_job_id_from_file(file_path):
    """
    Generate a job ID based on the .cwl file path.

    :param file_path: The path to the .cwl file.
    :return: A job ID.
    """
    # Example: use the file name (without extension) as job ID
    return os.path.splitext(os.path.basename(file_path))[0]

def get_result_by_job_id(job_id):
    """
    Retrieve the result for a given job ID.

    :param job_id: The job ID.
    :return: The result of the job.
    """
    # Implement this function to retrieve the result
    # For example, querying your result database or using Celery result backends
    # Assuming you store results in a dictionary or database
    result = {}  # Replace with actual result retrieval logic
    return result


# Example usage
if __name__ == "__main__":
    input_file = WORKFLOW_DIR
    if run_and_compare_all_cwls(input_file):
        print("All results are identical.")
    else:
        print("There are differences in results.")
