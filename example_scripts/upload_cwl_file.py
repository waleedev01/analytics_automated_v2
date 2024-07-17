import requests
import os
import sys
import django
current_dir = os.path.dirname(os.path.realpath(__file__))


project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analytics_automated_project.settings.dev')
django.setup()



from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
# URL endpoint for uploading CWL file
url = 'http://127.0.0.1:8000/analytics_automated/submission.json'

# Specify the file path of task1.cwl
cwl_file_path = '/home/gty/vv-project/cavid/analytics_automated_v2/analytics_automated/tests/example_cwl_files/test2.cwl'

input_file_path = '/home/gty/vv-project/cavid/analytics_automated_v2/example_scripts/input.txt'

# Prepare payload for file upload
files = {
    'input_data': ('input.txt', open(input_file_path, 'rb'))
}

# Additional data for the submission
data = {
    'job': 'test2.cwl',  # Assuming 'psipred' is the job identifier
    'submission_name': 'memembed2_submission',  # Name for the submission
    'email': '1115428019@ucl.ac.uk',  # Email associated with the submission,
}
test = []
#read_cwl_file(cwl_file_path,'test2.cwl',test)
# Make POST request to upload the file
response = requests.post(url, data=data, files=files)

# Print the response content
print(response.text)

