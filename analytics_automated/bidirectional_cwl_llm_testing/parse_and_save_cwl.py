import os
import logging
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
import time

# Setup logging
logger = logging.getLogger(__name__)

def parse_and_save_cwl_files(input_dir, num_files = None, valid = None):
    results = []
    file_list = os.listdir(input_dir)
    
    logger.info(f"Starting parsing and saving CWL files in directory: {file_list}")

    # Record the start time
    start_time = time.time()
    count = 0

    if valid is not None:
        if valid:
            keyword = '_valid_'
        else:
            keyword = '_invalid_'
    else:
        keyword = None
    
    for file_name in file_list:
        if num_files is not None and count == num_files:
            break

        if file_name.endswith('.cwl') and (keyword is None or keyword in file_name):
            count += 1
            cwl_path = os.path.join(input_dir, file_name)
            logger.debug(f"Processing file: {file_name}")
            
            try:
                messages = []
                result = read_cwl_file(cwl_path, file_name, messages)
                
                if result:
                    logger.info(f"Successfully parsed and saved file: {file_name}")
                    results.append({
                        'file_name': file_name,
                        'step': 'parsing_saving',
                        'result': 'success',
                        'message': ''
                    })
                else:
                    logger.warning(f"Failed to parse and save file: {file_name}. Messages: {messages}")
                    results.append({
                        'file_name': file_name,
                        'step': 'parsing_saving',
                        'result': 'failure',
                        'message': "; ".join(messages)
                    })
            
            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}")
                results.append({
                    'file_name': file_name,
                    'step': 'parsing_saving',
                    'result': 'failure',
                    'message': str(e)
                })
    
    # Record the end time
    end_time = time.time()

    # Calculate the execution time
    execution_time = (end_time - start_time) * 1000
    
    logger.info(f"Completed parsing and saving CWL files. Total files processed: {len(results)}")
    return results, execution_time

if __name__ == "__main__":
    parse_and_save_cwl_files('generated_cwl_files_valid')
