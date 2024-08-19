import subprocess
import logging
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def run_memembed_task(input_file, output_file):
    """
    Executes the MemEmbed tool with the given input file and writes the result to the output file.

    Args:
        input_file (str): Path to the input file required by MemEmbed.
        output_file (str): Path to the output file where MemEmbed's result will be written.

    Returns:
        int: Return code from the MemEmbed process:
            - 0 indicates successful execution.
            - Non-zero indicates failure or errors during execution.
    """
    work_dir = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/tasks/MemEmbed-master/bin'
    
    # 
    command = [
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/tasks/MemEmbed-master/bin/memembed',
        '-s', '1',
        '-b',
        '-n', '8',  #
        input_file
    ]
    
  
    try:
        result = subprocess.run(command, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        if result.stderr:
            logging.error(f"Error output: {result.stderr}")
        
        return result.returncode
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return -1

@app.task
def run_memembed_task(input_file, output_file):
    """
    Celery task to run the MemEmbed tool asynchronously using an input file, and saves the result to an output file.

    Args:
        input_file (str): Path to the input file for MemEmbed.
        output_file (str): Path to the output file where MemEmbed's output will be written.

    Returns:
        int: The return code from the MemEmbed execution:
            - 0 indicates success.
            - Non-zero indicates failure or error during execution.
    """
    work_dir = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/tasks/MemEmbed-master/bin'
    
    # 
    command = [
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/tasks/MemEmbed-master/bin/memembed',
        '-s', '1',
        '-b',
        '-n', '8',  #
        input_file
    ]
    
  
    try:
        result = subprocess.run(command, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        if result.stderr:
            logging.error(f"Error output: {result.stderr}")
        
        return result.returncode
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        return -1



run_memembed_task('/home/gty/vv-project/celery-requirement/analytics_automated_v2/tasks/MemEmbed-master/examples/2x2v.pdb','test.txt')

