import subprocess
import logging
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def run_memembed_task(input_file, output_file):
    
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

