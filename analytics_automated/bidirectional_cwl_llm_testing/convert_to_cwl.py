import os
import logging
import difflib
from django.core.exceptions import ObjectDoesNotExist
from analytics_automated.cwl_utils.reconstruct_task import reconstruct_task_cwl
from analytics_automated.cwl_utils.reconstruct_workflow import reconstruct_workflow_cwl
from ruamel.yaml import YAML
import csv

# Setup logging
logger = logging.getLogger(__name__)

def save_cwl_file(cwl_content, file_path):
    """
    Save CWL content to a file.
    """
    logger.debug(f"Saving CWL file: {file_path}")
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096

    try:
        with open(file_path, 'w') as file:
            yaml.dump(cwl_content, file)
        logger.debug(f"Successfully saved CWL file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save CWL file {file_path}: {str(e)}")

def compare_files(original_file_path, reconstructed_file_path):
    """
    Compare two files and return a list of differences.
    """
    with open(original_file_path, 'r') as original_file, open(reconstructed_file_path, 'r') as reconstructed_file:
        original_lines = original_file.readlines()
        reconstructed_lines = reconstructed_file.readlines()
        
    diff = list(difflib.unified_diff(original_lines, reconstructed_lines, fromfile='original', tofile='reconstructed'))
    return diff

def read_file_content(file_path):
    """
    Read the content of a file and return it as a string.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def write_results_to_csv(results, csv_path):
    """
    Write the results of the conversion to a CSV file.
    """
    fieldnames = [
        'file_name', 'step', 'result', 'expected_is_valid', 'expected_error',
        'got_is_valid', 'got_error', 'validity_matches', 'exact_error_matches',
        'partial_error_matches', 'expected_str', 'got_str', 'differences',
        'message', 'source_file', 'target_file', 'original_content', 'reconstructed_content'
    ]

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def convert_to_cwl_files(output_dir):
    """
    Convert database entries to CWL files and compare them with the original files.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    results = []

    from ..models import Job, Task  # Import both models

    # Path to the directory containing the original generated CWL files
    generated_cwl_dir = 'analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid'
    
    # Get all valid CWL files in the directory
    valid_cwl_files = [f for f in os.listdir(generated_cwl_dir) if f.endswith('.cwl')]
    
    for cwl_file in valid_cwl_files:
        job_name = os.path.splitext(cwl_file)[0]

        try:
            # Check if the CWL file is a Workflow or CommandLineTool
            original_file_path = os.path.join(generated_cwl_dir, cwl_file)
            original_content = read_file_content(original_file_path)  # Read original file content
            is_workflow = 'class: Workflow' in original_content

            if is_workflow:
                # Handle Workflow
                try:
                    # Check if job exists in the database
                    job = Job.objects.get(name=job_name)
                    logger.info(f"Found job in database: {job_name}")

                    # Define the path to save the reconstructed workflow
                    workflow_file_path = os.path.join(output_dir, f"{job.name}.cwl")

                    # Reconstruct workflow from the database
                    reconstruct_workflow_cwl(job, workflow_file_path)

                    # Compare with the original CWL file
                    diff = compare_files(original_file_path, workflow_file_path)
                    comparison_result = 'success' if not diff else 'differences found'

                    # Read reconstructed file content
                    reconstructed_content = read_file_content(workflow_file_path)

                    results.append({
                        'file_name': job.name,
                        'step': 'conversion',
                        'result': comparison_result,
                        'expected_is_valid': 'TRUE',  # Assuming original files are valid
                        'expected_error': '',  # No expected error
                        'got_is_valid': 'TRUE' if not diff else 'FALSE',
                        'got_error': '' if not diff else 'Differences found',
                        'validity_matches': True,
                        'exact_error_matches': True if not diff else False,
                        'partial_error_matches': True if not diff else False,
                        'expected_str': '',  # Placeholder for expected string representation
                        'got_str': '',  # Placeholder for got string representation
                        'differences': '\n'.join(diff) if diff else '',  # Convert list to string
                        'message': 'Conversion successful' if not diff else 'Differences found in conversion',
                        'source_file': original_file_path,
                        'target_file': workflow_file_path,
                        'original_content': original_content,  # Add original content
                        'reconstructed_content': reconstructed_content  # Add reconstructed content
                    })

                    # Reconstruct tasks for each step in the workflow
                    for step in job.steps.all():  # Correct reverse relation
                        task_file_path = os.path.join(output_dir, f"{step.task.name}.cwl")
                        reconstruct_task_cwl(step.task, task_file_path)

                        # Compare with the original task file if it exists
                        original_task_file_path = os.path.join(generated_cwl_dir, f"{step.task.name}.cwl")
                        if os.path.exists(original_task_file_path):
                            task_diff = compare_files(original_task_file_path, task_file_path)
                            task_comparison_result = 'success' if not task_diff else 'differences found'

                            # Read reconstructed task content
                            reconstructed_task_content = read_file_content(task_file_path)

                            results.append({
                                'file_name': step.task.name,
                                'step': 'conversion',
                                'result': task_comparison_result,
                                'expected_is_valid': 'TRUE',  # Assuming original files are valid
                                'expected_error': '',  # No expected error
                                'got_is_valid': 'TRUE' if not task_diff else 'FALSE',
                                'got_error': '' if not task_diff else 'Differences found',
                                'validity_matches': True,
                                'exact_error_matches': True if not task_diff else False,
                                'partial_error_matches': True if not task_diff else False,
                                'expected_str': '',  # Placeholder for expected string representation
                                'got_str': '',  # Placeholder for got string representation
                                'differences': '\n'.join(task_diff) if task_diff else '',
                                'message': 'Conversion successful' if not task_diff else 'Differences found in conversion',
                                'source_file': original_task_file_path,
                                'target_file': task_file_path,
                                'original_content': read_file_content(original_task_file_path),  # Add original task content
                                'reconstructed_content': reconstructed_task_content  # Add reconstructed task content
                            })
                except ObjectDoesNotExist as e:
                    error_message = f"Error converting job '{job_name}': {e}"
                    logger.error(error_message)
                    results.append({
                        'file_name': job_name,
                        'step': 'conversion',
                        'result': 'failure',
                        'expected_is_valid': 'TRUE',
                        'expected_error': '',
                        'got_is_valid': 'FALSE',
                        'got_error': str(e),
                        'validity_matches': False,
                        'exact_error_matches': False,
                        'partial_error_matches': False,
                        'expected_str': '',
                        'got_str': '',
                        'differences': '',
                        'message': error_message,
                        'source_file': original_file_path,
                        'target_file': 'N/A',
                        'original_content': original_content,  # Add original content
                        'reconstructed_content': ''  # No reconstructed content due to failure
                    })
            else:
                # Handle CommandLineTool
                try:
                    # Check if task exists in the database
                    task = Task.objects.get(name=job_name)
                    logger.info(f"Found task in database: {job_name}")

                    # Define the path to save the reconstructed task
                    task_file_path = os.path.join(output_dir, f"{task.name}.cwl")

                    # Reconstruct task from the database
                    reconstruct_task_cwl(task, task_file_path)

                    # Compare with the original CWL file
                    diff = compare_files(original_file_path, task_file_path)
                    comparison_result = 'success' if not diff else 'differences found'

                    # Read reconstructed file content
                    reconstructed_content = read_file_content(task_file_path)

                    results.append({
                        'file_name': task.name,
                        'step': 'conversion',
                        'result': comparison_result,
                        'expected_is_valid': 'TRUE',  # Assuming original files are valid
                        'expected_error': '',  # No expected error
                        'got_is_valid': 'TRUE' if not diff else 'FALSE',
                        'got_error': '' if not diff else 'Differences found',
                        'validity_matches': True,
                        'exact_error_matches': True if not diff else False,
                        'partial_error_matches': True if not diff else False,
                        'expected_str': '',  # Placeholder for expected string representation
                        'got_str': '',  # Placeholder for got string representation
                        'differences': '\n'.join(diff) if diff else '',
                        'message': 'Conversion successful' if not diff else 'Differences found in conversion',
                        'source_file': original_file_path,
                        'target_file': task_file_path,
                        'original_content': original_content,  # Add original content
                        'reconstructed_content': reconstructed_content  # Add reconstructed content
                    })
                except ObjectDoesNotExist as e:
                    error_message = f"Error converting task '{job_name}': {e}"
                    logger.error(error_message)
                    results.append({
                        'file_name': job_name,
                        'step': 'conversion',
                        'result': 'failure',
                        'expected_is_valid': 'TRUE',
                        'expected_error': '',
                        'got_is_valid': 'FALSE',
                        'got_error': str(e),
                        'validity_matches': False,
                        'exact_error_matches': False,
                        'partial_error_matches': False,
                        'expected_str': '',
                        'got_str': '',
                        'differences': '',
                        'message': error_message,
                        'source_file': original_file_path,
                        'target_file': 'N/A',
                        'original_content': original_content,  # Add original content
                        'reconstructed_content': ''  # No reconstructed content due to failure
                    })

        except Exception as e:
            error_message = f"Unexpected error processing '{cwl_file}': {e}"
            logger.error(error_message)
            results.append({
                'file_name': cwl_file,
                'step': 'conversion',
                'result': 'failure',
                'expected_is_valid': 'TRUE',
                'expected_error': '',
                'got_is_valid': 'FALSE',
                'got_error': str(e),
                'validity_matches': False,
                'exact_error_matches': False,
                'partial_error_matches': False,
                'expected_str': '',
                'got_str': '',
                'differences': '',
                'message': error_message,
                'source_file': original_file_path,
                'target_file': 'N/A',
                'original_content': read_file_content(original_file_path),  # Add original content
                'reconstructed_content': ''  # No reconstructed content due to error
            })

    return results

if __name__ == "__main__":
    output_directory = 'analytics_automated/bidirectional_cwl_llm_testing/converted_cwl_files'
    results = convert_to_cwl_files(output_directory)
    # Write results to CSV
    csv_path = 'analytics_automated/bidirectional_cwl_llm_testing/validation_results/validation_results.csv'
    write_results_to_csv(results, csv_path)
    # Log results
    for result in results:
        logger.info(result)
