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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        # parsing_results = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files')
        logging.info("Step 3 completed")

        logging.info("Step 4: Converting database entries to CWL files")
        # conversion_results = convert_to_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/converted_cwl_files')
        logging.info("Step 4 completed")

        results.extend(validation_results)
        # results.extend(parsing_results)
        # results.extend(conversion_results)

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

    write_results_to_csv(results, 'analytics_automated/bidirectional_cwl_llm_testing/pipeline_results.csv')

def write_results_to_csv(results, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = [
            'file_name', 'step', 'result',
            'expected_is_valid', 'expected_error',
            'got_is_valid', 'got_error',
            'matches_valid_count', 'matches_error_count', 'matches_partial_error',
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

                # Check for full error match
                matches_valid_count = expected_is_valid == got_is_valid
                matches_error_count = expected_error == got_error

                # Check for partial error match (if the expected error is a substring of the got error)
                matches_partial_error = (expected_error in got_error) if expected_error and got_error else False

                logging.debug(f"Full error match: {matches_error_count}")
                logging.debug(f"Partial error match: {matches_partial_error}")

                writer.writerow({
                    'file_name': result.get('file_name'),
                    'step': result.get('step'),
                    'result': result.get('result'),
                    'expected_is_valid': expected_is_valid,
                    'expected_error': expected_error,
                    'got_is_valid': got_is_valid,
                    'got_error': got_error,
                    'matches_valid_count': matches_valid_count,
                    'matches_error_count': matches_error_count,
                    'matches_partial_error': matches_partial_error,
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
                    'matches_valid_count': False,
                    'matches_error_count': False,
                    'matches_partial_error': False,
                    'expected_str': result.get('expected_str'),
                    'got_str': result.get('got_str')
                })

if __name__ == "__main__":
    run_pipeline()