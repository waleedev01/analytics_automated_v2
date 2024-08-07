import requests
import os
import sys
import django
import time
import logging
from flask import Flask, request, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Django environment
current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_automated_project.settings.dev')
django.setup()

# Import your CWL parser function
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    start_time = time.time()
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    cwl_file_path = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen-cwl/'
    file = request.files['file']
    test = []
    cwl_file_path = cwl_file_path + str(file.filename) 
    if file.filename.endswith('.cwl'):
        read_cwl_file(cwl_file_path,file,test)  
        response_time = (time.time() - start_time) * 1000  
        return jsonify({'message': 'File processed', 'response_time': response_time}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(port=8000)
