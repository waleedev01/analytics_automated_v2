import os
import time
import json
import pytest
import sys
import django
from celery.result import AsyncResult
from celery import chain, chord

# Setup Django environment
current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_automated_project.settings.dev')
django.setup()


from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

# Directory containing the CWL files
#CWL_DIR = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen-cwl/'
CWL_DIR = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/example_cwl_files/'

@pytest.fixture(scope='module')
def setup_cwl_files():
    """
    Set up any required test fixtures for CWL file execution.
    This function can be used to initialize mock data, prepare the test environment,
    or configure necessary files and settings.
    
    Note: This function is currently a placeholder and does not perform any operations.
    """
    pass

def execute_cwl_file(cwl_file_path):
    """
    Execute a CWL file using Celery and check if it completes successfully.
    
    Args:
        cwl_file_path (str): Path to the CWL file to be executed.
        
    Returns:
        tuple: A tuple containing:
            - bool: Indicates whether the CWL file was executed successfully.
            - str: Message providing the result of the execution or the error encountered.
    """
    with open(cwl_file_path, 'r') as f:
        cwl_data = f.read()
    test = []
    # Parse CWL file to generate Celery tasks (or chains/chords)
    tasks = read_cwl_file(cwl_file_path,cwl_data,test)
    
    if not tasks:
        return False, "No tasks generated from CWL file."
    
    try:
        # Create a Celery chain or chord depending on the parsed tasks
        if isinstance(tasks, list):  # Assuming tasks are in list format
            result = chain(*tasks)()
        else:
            result = chord(tasks)()
        
        # Wait for the result with a timeout
        start_time = time.time()
        while not result.ready():
            time.sleep(1)
            if time.time() - start_time > 60:  # Timeout after 60 seconds
                return False, "Task execution timeout."
        
        if result.status == 'SUCCESS':
            return True, result.result
        else:
            return False, result.result
    except Exception as e:
        return False, str(e)

def test_cwl_execution():
    """
    Test execution of all CWL files in the specified directory.
    
    Args:
        None
    
    Returns:
        None
    
    This function:
        - Iterates through all CWL files in the specified directory.
        - Executes each CWL file using the `execute_cwl_file` function.
        - Logs the results to a JSON file.
        - Prints a summary of the test results including total files tested, 
          number of successful executions, and failure rate.
    """
    cwl_files = [f for f in os.listdir(CWL_DIR) if f.endswith('.cwl')]
    results = {}
    
    for cwl_file in cwl_files:
        cwl_file_path = os.path.join(CWL_DIR, cwl_file)
        success, message = execute_cwl_file(cwl_file_path)
        results[cwl_file] = (success, message)
        
        assert success, f"CWL file {cwl_file} failed with message: {message}"
    
    # Log results to a file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Print summary
    successful = sum(1 for success, _ in results.values() if success)
    total = len(results)
    print(f"Total CWL files tested: {total}")
    print(f"Successfully executed: {successful}")
    print(f"Failure rate: {(total - successful) / total * 100:.2f}%")
