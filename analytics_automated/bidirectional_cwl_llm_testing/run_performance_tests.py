import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'analytics_automated_project.settings.dev'

import django
django.setup()

# from analytics_automated.bidirectional_cwl_llm_testing.generate_cwl_files import generate_cwl_files
from analytics_automated.bidirectional_cwl_llm_testing.parse_and_save_cwl import parse_and_save_cwl_files

# Setup logging
logger = logging.getLogger(__name__)

def run_pipeline():
    """
    Execute the pipeline for parsing and saving CWL files of varying validity to the database, measuring execution times.

    The pipeline performs the following steps:
    1. Parses and saves 20 valid CWL files to the database.
    2. Parses and saves 50 valid CWL files to the database.
    3. Parses and saves 80 valid CWL files to the database.
    4. Parses and saves 20 invalid CWL files to the database.
    5. Parses and saves 50 invalid CWL files to the database.
    6. Parses and saves 80 invalid CWL files to the database.

    This process is repeated 5 times to obtain average execution times for each scenario. 
    The average execution times are logged for analysis.

    Logs detailed information about each step, including execution times and any errors encountered.
    """
    results = []

    try:
        execution_time_20_valid_arr = []
        execution_time_50_valid_arr = []
        execution_time_80_valid_arr = []
        execution_time_20_invalid_arr = []
        execution_time_50_invalid_arr = []
        execution_time_80_invalid_arr = []

        for i in range(5):
            logging.info("Step 1: Generating CWL files")
            # generate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 10)
            logging.info("Step 1 completed")

            logging.info("Step 2: Parsing and saving 20 valid CWL files to database")
            _, execution_time_20_valid = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 20, True)
            execution_time_20_valid_arr.append(execution_time_20_valid)
            logging.info("Step 2 completed")

            logging.info("Step 3: Parsing and saving 50 valid CWL files to database")
            _, execution_time_50_valid = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 50, True)
            execution_time_50_valid_arr.append(execution_time_50_valid)
            logging.info("Step 3 completed")

            logging.info("Step 4: Parsing and saving 80 valid CWL files to database")
            _, execution_time_80_valid = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 80, True)
            execution_time_80_valid_arr.append(execution_time_80_valid)
            logging.info("Step 4 completed")

            logging.info("Step 5: Parsing and saving 20 invalid CWL files to database")
            _, execution_time_20_invalid = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 20, False)
            execution_time_20_invalid_arr.append(execution_time_20_invalid)
            logging.info("Step 5 completed")

            logging.info("Step 6: Parsing and saving 50 invalid CWL files to database")
            _, execution_time_50_invalid = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 50, False)
            execution_time_50_invalid_arr.append(execution_time_50_invalid)
            logging.info("Step 6 completed")

            logging.info("Step 7: Parsing and saving 50 invalid CWL files to database")
            _, execution_time_80_invalid = parse_and_save_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 80, False)
            execution_time_80_invalid_arr.append(execution_time_80_invalid)
            logging.info("Step 7 completed")

        logging.info(f"Average Total Execution Time for 20 valid CWL files: {sum(execution_time_20_valid_arr) / 5} miliseconds")
        logging.info(f"Average Total Execution Time for 50 valid CWL files: {sum(execution_time_50_valid_arr) / 5} miliseconds")
        logging.info(f"Average Total Execution Time for 80 valid CWL files: {sum(execution_time_80_valid_arr) / 5} miliseconds")
        logging.info(f"Average Total Execution Time for 20 invalid CWL files: {sum(execution_time_20_invalid_arr) / 5} miliseconds")
        logging.info(f"Average Total Execution Time for 50 invalid CWL files: {sum(execution_time_50_invalid_arr) / 5} miliseconds")
        logging.info(f"Average Total Execution Time for 80 invalid CWL files: {sum(execution_time_80_invalid_arr) / 5} miliseconds")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    run_pipeline()
