import os
import logging
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
import time

# Setup logging
logger = logging.getLogger(__name__)

def parse_and_save_cwl_files(input_dir, num_files = None, valid = None):
    """
    Parse and save CWL files from the given directory. The function processes
    the CWL files in the specified directory, filters them based on validity, 
    and limits the number of files processed if specified. Each file is parsed
    using the `read_cwl_file` function, and the results are logged.

    Args:
        input_dir (str): Directory path containing the CWL files to be processed.
        num_files (int, optional): Maximum number of files to process. If None, 
                                   all files in the directory are processed.
        valid (bool, optional): If True, only valid files (containing '_valid_' 
                                in the name) are processed. If False, only invalid
                                files ('_invalid_' in the name) are processed. 
                                If None, both valid and invalid files are processed.

    Returns:
        results (list): A list of dictionaries containing details about the processing 
                        result for each file (file name, step, result, message).
        execution_time (float): The time taken to process the files in milliseconds.

    Raises:
        Exception: Logs any exceptions that occur during file processing and includes 
                   them in the result message for the corresponding file.
    """
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
    parse_and_save_cwl_files('generated_cwl_files')
