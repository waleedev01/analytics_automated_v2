import os
import json
import logging
import yaml
from analytics_automated.cwl_utils.cwl_schema_validator import CWLSchemaValidator

# Setup logging
logger = logging.getLogger(__name__)

def validate_cwl_files(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    validator = CWLSchemaValidator()
    results = []

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.cwl'):
            file_path = os.path.join(input_dir, file_name)
            expected_path = os.path.join(input_dir, f"{file_name}.expected")
            
            try:
                logger.debug(f"Loading CWL file: {file_path}")
                with open(file_path, 'r') as file:
                    cwl_data = yaml.safe_load(file)
                logger.debug(f"CWL data loaded successfully: {file_path}")

                logger.debug(f"Loading expected result file: {expected_path}")
                with open(expected_path, 'r') as file:
                    expected_result = json.load(file)
                logger.debug(f"Expected result loaded successfully: {expected_path}")

                logger.debug(f"Validating CWL data for file: {file_path}")
                is_valid, message = validator.validate_cwl(cwl_data)
                logger.debug(f"Validation completed for file: {file_path} with result: {is_valid}, message: {message}")

                expected_is_valid = expected_result.get("is_valid")
                expected_error = expected_result.get("error")

                # Ensure we compare the full error message to catch all validation errors
                if is_valid != expected_is_valid or (expected_error and not message.startswith(expected_error)):
                    result_status = "failure"
                else:
                    result_status = "success"

                result = {
                    "file_name": file_name,
                    "step": "validation",
                    "result": result_status,
                    "expected": expected_result,
                    "expected_str": json.dumps(expected_result),
                    "got": {
                        "is_valid": is_valid,
                        "error": message
                    },
                    "got_str": json.dumps({
                        "is_valid": is_valid,
                        "error": message
                    })
                }
                results.append(result)

                output_path = os.path.join(output_dir, f"{file_name}.result")
                logger.debug(f"Writing result to file: {output_path}")
                with open(output_path, 'w') as file:
                    json.dump(result, file, indent=4)
                logger.info(f"Result written successfully for file: {file_name}")

            except Exception as e:
                logger.error(f"Error processing file {file_name}: {e}", exc_info=True)

    return results

if __name__ == "__main__":
    try:
        logger.info("Starting CWL file validation process.")
        validate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 'analytics_automated/bidirectional_cwl_llm_testing/validation_results')
        logger.info("CWL file validation process completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
