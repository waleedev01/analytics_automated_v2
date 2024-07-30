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

# Setup logging
logger = logging.getLogger(__name__)

def run_pipeline():
    results = []

    try:
        logging.info("Step 1: Generating CWL files")
        # generate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 10)
        logging.info("Step 1 completed")

        logging.info("Step 2: Validating CWL files")
        validation_results = validate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 'analytics_automated/bidirectional_cwl_llm_testing/validation_results')
        logging.info("Step 2 completed")

        logging.info("Step 3: Parsing and saving CWL files to database")
        parsing_results = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files')
        logging.info("Step 3 completed")

        logging.info("Step 4: Converting database entries to CWL files")
        # conversion_results = convert_to_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/converted_cwl_files')
        logging.info("Step 4 completed")

        results.extend(validation_results)
        # results.extend(parsing_results)
        # results.extend(conversion_results)

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

    write_results_to_csv(results, 'analytics_automated/bidirectional_cwl_llm_testing/validation_results/validation_results.csv')

def write_results_to_csv(results, csv_path):
    total_files_generated = len(results)
    total_validity_matches = 0
    total_exact_error_matches = 0
    total_partial_error_matches = 0

    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = [
            'file_name', 'step', 'result',
            'expected_is_valid', 'expected_error',
            'got_is_valid', 'got_error',
            'validity_matches', 'exact_error_matches', 'partial_error_matches',
            'expected_str', 'got_str'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            logging.info(f"Processing result for file: {result.get('file_name')}")
            logging.debug(f"Result: {result}")

            try:
                expected = result.get('expected', {})
                got = result.get('got', {})

                expected_is_valid = expected.get('is_valid')
                expected_error = expected.get('error')

                got_is_valid = got.get('is_valid')
                got_error = got.get('error')

                logging.debug(f"Expected is_valid: {expected_is_valid}, Got is_valid: {got_is_valid}")
                logging.debug(f"Expected error: {expected_error}")
                logging.debug(f"Got error: {got_error}")

                # Check for validity match
                validity_matches = expected_is_valid == got_is_valid
                # Check for exact error match
                exact_error_matches = expected_error == got_error
                # Check for partial error match (if the expected error is a substring of the got error)
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
                    'expected_str': result.get('expected_str'),
                    'got_str': result.get('got_str')
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
                    'expected_str': result.get('expected_str'),
                    'got_str': result.get('got_str')
                })

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
