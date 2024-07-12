import os
import json
import logging
from analytics_automated.cwl_utils.cwl_schema_validator import CWLSchemaValidator

# Setup logging
logger = logging.getLogger(__name__)

def validate_cwl_files(input_dir, output_dir):
    results = []
    validator = CWLSchemaValidator()
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.cwl'):
            cwl_path = os.path.join(input_dir, file_name)
            expected_path = os.path.join(input_dir, f'{file_name}.expected')
            
            with open(cwl_path, 'r') as f:
                cwl_data = f.read()

            with open(expected_path, 'r') as f:
                expected_result = json.load(f)

            is_valid, message = validator.validate_cwl(cwl_data)
            validation_result = {
                "is_valid": is_valid,
                "error": None if is_valid else message
            }

            result_file = os.path.join(output_dir, f'{file_name}.result')
            with open(result_file, 'w') as f:
                json.dump(validation_result, f)

            if validation_result != expected_result:
                logging.error(f"Validation result for {file_name} does not match expected result")
                results.append({
                    'file_name': file_name,
                    'step': 'validation',
                    'result': 'failure',
                    'message': f"Expected: {expected_result}, Got: {validation_result}"
                })
            else:
                logging.info(f"Validation successful for {file_name}")
                results.append({
                    'file_name': file_name,
                    'step': 'validation',
                    'result': 'success',
                    'message': ''
                })

    return results

if __name__ == "__main__":
    validate_cwl_files('generated_cwl_files', 'validation_results')
