import os
import logging
#from analytics_automated.cwl_utils.cwl_parser import convert_to_cwl

# Setup logging
logger = logging.getLogger(__name__)

def convert_to_cwl_files(output_dir):
    results = []
    # Assuming convert_to_cwl() function does the conversion and returns a dictionary
    # with file names as keys and conversion statuses as values.
    conversion_statuses = convert_to_cwl()
    for file_name, status in conversion_statuses.items():
        if status['success']:
            results.append({
                'file_name': file_name,
                'step': 'conversion',
                'result': 'success',
                'message': ''
            })
        else:
            results.append({
                'file_name': file_name,
                'step': 'conversion',
                'result': 'failure',
                'message': status['error']
            })

    return results

if __name__ == "__main__":
    convert_to_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/converted_cwl_files')
