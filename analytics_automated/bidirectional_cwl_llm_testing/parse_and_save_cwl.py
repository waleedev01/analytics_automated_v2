import os
import logging
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

# Setup logging
logger = logging.getLogger(__name__)

def parse_and_save_cwl_files(input_dir):
    results = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.cwl'):
            cwl_path = os.path.join(input_dir, file_name)
            messages = []
            result = read_cwl_file(cwl_path, file_name, messages)
            if result:
                results.append({
                    'file_name': file_name,
                    'step': 'parsing_saving',
                    'result': 'success',
                    'message': ''
                })
            else:
                results.append({
                    'file_name': file_name,
                    'step': 'parsing_saving',
                    'result': 'failure',
                    'message': "; ".join(messages)
                })

    return results

if __name__ == "__main__":
    parse_and_save_cwl_files('generated_cwl_files')
