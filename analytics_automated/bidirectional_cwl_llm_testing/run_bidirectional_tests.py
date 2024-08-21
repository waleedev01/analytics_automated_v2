import logging
import sys
import os
import csv
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'analytics_automated_project.settings.dev'

import django
django.setup()

from analytics_automated.bidirectional_cwl_llm_testing.generate_cwl_files import generate_cwl_files
from analytics_automated.bidirectional_cwl_llm_testing.validate_cwl_files import validate_cwl_files
from analytics_automated.bidirectional_cwl_llm_testing.parse_and_save_cwl import parse_and_save_cwl_files
from analytics_automated.bidirectional_cwl_llm_testing.convert_to_cwl import convert_to_cwl_files

# Setup logging
logger = logging.getLogger(__name__)

def run_pipeline():
    """
    Execute the pipeline for generating, validating, parsing, saving, and converting CWL files.
    
    This function performs the following steps:
    1. Generates CWL files.
    2. Validates the generated CWL files.
    3. Parses and saves the CWL files to a database.
    4. Converts database entries back to CWL files.
    
    Results from each step are collected and written to a CSV file.
    
    Logs detailed information about the process and any errors encountered.
    """
    results = []

    try:
        logging.info("Step 1: Generating CWL files")
        # generate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 10)
        logging.info("Step 1 completed")

        logging.info("Step 2: Validating CWL files")
        validation_results = validate_cwl_files(
            'analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 
            'analytics_automated/bidirectional_cwl_llm_testing/validation_results'
        )
        logging.info("Step 2 completed")

        logging.info("Step 3: Parsing and saving CWL files to database")
        parsing_results, _ = parse_and_save_cwl_files(
            'analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid'
        )
        logging.info("Step 3 completed")

        logging.info("Step 4: Converting database entries to CWL files")
        conversion_results = convert_to_cwl_files(
            'analytics_automated/bidirectional_cwl_llm_testing/converted_cwl_files'
        )
        logging.info("Step 4 completed")

        # Combine all results
        results.extend(validation_results)
        results.extend(parsing_results)
        results.extend(conversion_results)

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

    write_results_to_csv(results, 'analytics_automated/bidirectional_cwl_llm_testing/validation_results/validation_results.csv')

def write_results_to_csv(results, csv_path):
    """
    Write the results of each step of the pipeline to a CSV file and a summary file.

    Args:
        results (list): A list of dictionaries containing the results from the pipeline steps.
        csv_path (str): The file path where the results should be written.

    Raises:
        Exception: If there is an error writing to the CSV file.
    
    The CSV file contains columns for file details, validation results, and error matches.
    An additional summary text file is created with overall statistics.
    """
    """
    Writes the results of each step of the pipeline to a CSV file.
    """
    total_files_generated = len(results)
    total_validity_matches = 0
    total_exact_error_matches = 0
    total_partial_error_matches = 0

    # Define CSV fieldnames
    fieldnames = [
        'file_name', 'step', 'result',
        'expected_is_valid', 'expected_error',
        'got_is_valid', 'got_error',
        'validity_matches', 'exact_error_matches', 'partial_error_matches',
        'expected_str', 'got_str', 'original_content', 'reconstructed_content',
        'message', 'source_file', 'target_file'
    ]

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            logging.info(f"Processing result for file: {result.get('file_name')}")
            logging.debug(f"Result: {result}")

            try:
                # Extract result details
                expected = result.get('expected', {})
                got = result.get('got', {})

                expected_is_valid = expected.get('is_valid', 'N/A')
                expected_error = expected.get('error', 'N/A')

                got_is_valid = got.get('is_valid', 'N/A')
                got_error = got.get('error', 'N/A')

                # Determine validity and error matches
                validity_matches = expected_is_valid == got_is_valid
                exact_error_matches = expected_error == got_error
                partial_error_matches = (expected_error in got_error) if expected_error and got_error else False

                logging.debug(f"Validity match: {validity_matches}")
                logging.debug(f"Exact error match: {exact_error_matches}")
                logging.debug(f"Partial error match: {partial_error_matches}")

                if validity_matches:
                    total_validity_matches += 1
                if exact_error_matches:
                    total_exact_error_matches += 1
                if partial_error_matches:
                    total_partial_error_matches += 1

                # Write the result to the CSV file
                writer.writerow({
                    'file_name': result.get('file_name'),
                    'step': result.get('step'),
                    'result': result.get('result'),
                    'expected_is_valid': expected_is_valid,
                    'expected_error': expected_error,
                    'got_is_valid': got_is_valid,
                    'got_error': got_error,
                    'validity_matches': validity_matches,
                    'exact_error_matches': exact_error_matches,
                    'partial_error_matches': partial_error_matches,
                    'expected_str': result.get('expected_str', 'N/A'),
                    'got_str': result.get('got_str', 'N/A'),
                    'original_content': result.get('original_content', ''),
                    'reconstructed_content': result.get('reconstructed_content', ''),
                    'message': result.get('message', ''),
                    'source_file': result.get('source_file', 'N/A'),
                    'target_file': result.get('target_file', 'N/A')
                })

            except Exception as e:
                logging.error(f"Error processing result for file {result.get('file_name')}: {e}")
                writer.writerow({
                    'file_name': result.get('file_name'),
                    'step': result.get('step'),
                    'result': result.get('result'),
                    'expected_is_valid': None,
                    'expected_error': None,
                    'got_is_valid': None,
                    'got_error': None,
                    'validity_matches': False,
                    'exact_error_matches': False,
                    'partial_error_matches': False,
                    'expected_str': result.get('expected_str', 'N/A'),
                    'got_str': result.get('got_str', 'N/A'),
                    'original_content': '',
                    'reconstructed_content': '',
                    'message': result.get('message', ''),
                    'source_file': result.get('source_file', 'N/A'),
                    'target_file': result.get('target_file', 'N/A')
                })

    # Log summary stats
    logging.info(f"Total CWL files generated: {total_files_generated}")
    logging.info(f"Total validity matches: {total_validity_matches}")
    logging.info(f"Total exact error matches: {total_exact_error_matches}")
    logging.info(f"Total partial error matches: {total_partial_error_matches}")

    # Write overall stats to a summary file
    with open(csv_path.replace('.csv', '_summary.txt'), 'w') as summary_file:
        summary_file.write(f"Total CWL files generated (The total number of CWL files generated): {total_files_generated}\n")
        summary_file.write(f"Total validity matches (The count of how many times our validation results matched the validity (i.e., valid or invalid) as expected by OpenAI): {total_validity_matches}\n")
        summary_file.write(f"Total exact error matches (The count of how many times our validation results matched the exact error message as expected by OpenAI): {total_exact_error_matches}\n")
        summary_file.write(f"Total partial error matches (The count of how many times our validation results had a partial error match (i.e., the expected error was a substring of the actual error)): {total_partial_error_matches}\n")

if __name__ == "__main__":
    run_pipeline()
