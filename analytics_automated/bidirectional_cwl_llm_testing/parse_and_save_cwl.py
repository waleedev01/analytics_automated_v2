import os
import logging
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

# Setup logging
logger = logging.getLogger(__name__)

def parse_and_save_cwl_files(input_dir):
    results = []
    
    logger.info(f"Starting parsing and saving CWL files in directory: {input_dir}")
    
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.cwl'):
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
    
    logger.info(f"Completed parsing and saving CWL files. Total files processed: {len(results)}")
    return results

if __name__ == "__main__":
    parse_and_save_cwl_files('generated_cwl_files')
