import logging
import sys
import os
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'analytics_automated_project.settings.dev'

import django
django.setup()

from analytics_automated.llm_testing.generate_cwl_files import generate_cwl_files
from analytics_automated.llm_testing.validate_cwl_files import validate_cwl_files
from analytics_automated.llm_testing.parse_and_save_cwl import parse_and_save_cwl_files
from analytics_automated.llm_testing.convert_to_cwl import convert_to_cwl_files

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    results = []

    try:
        logging.info("Step 1: Generating CWL files")
        generate_cwl_files('analytics_automated/llm_testing/generated_cwl_files', 10)
        logging.info("Step 1 completed")

        logging.info("Step 2: Validating CWL files")
        validation_results = validate_cwl_files('analytics_automated/llm_testing/generated_cwl_files', 'analytics_automated/llm_testing/validation_results')
        logging.info("Step 2 completed")

        logging.info("Step 3: Parsing and saving CWL files to database")
        parsing_results = parse_and_save_cwl_files('analytics_automated/llm_testing/generated_cwl_files')
        logging.info("Step 3 completed")

        logging.info("Step 4: Converting database entries to CWL files")
        #conversion_results = convert_to_cwl_files('analytics_automated/llm_testing/converted_cwl_files')
        logging.info("Step 4 completed")

        results.extend(validation_results)
        results.extend(parsing_results)
        results.extend(conversion_results)

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

    write_results_to_csv(results, 'analytics_automated/llm_testing/pipeline_results.csv')

def write_results_to_csv(results, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['file_name', 'step', 'result', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    run_pipeline()
