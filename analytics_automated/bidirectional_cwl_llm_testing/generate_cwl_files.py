import os
import json
import logging
from openai import OpenAI

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='')

# Define variables for prompts
VALID_CWL_VERSIONS = ['v1.0', 'v1.1', 'v1.2']
VALID_CWL_CLASSES = ['CommandLineTool', 'Workflow']
UNSUPPORTED_REQUIREMENTS = [
    'InlineJavascriptRequirement',
    'ResourceRequirement',
    'DockerRequirement',
]
FILE_TYPE = 'File'

def generate_cwl_file(prompt):
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating CWL file: {e}")
        raise

def generate_cwl_files(output_dir, num_files):
    os.makedirs(output_dir, exist_ok=True)

    prompts = [
        (f"Generate a valid CWL file with cwlVersion from {VALID_CWL_VERSIONS}, class from {VALID_CWL_CLASSES}, baseCommand, inputs, and outputs properly defined. "
         f"Ensure the class is CommandLineTool, includes a baseCommand, and only {FILE_TYPE} type is used for inputs and outputs.", 
         {"is_valid": True, "error": "CWL file is valid."}),
        (f"Generate a valid CWL file with cwlVersion from {VALID_CWL_VERSIONS}, class from {VALID_CWL_CLASSES}, baseCommand, inputs, and outputs properly defined. "
         f"Ensure the class is Workflow, includes steps, and only {FILE_TYPE} type is used for inputs and outputs.", 
         {"is_valid": True, "error": "CWL file is valid."}),
        ("Generate an invalid CWL file with missing 'cwlVersion'. Ensure it has 'class', 'inputs', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'cwlVersion' in CWL file"}),
        ("Generate an invalid CWL file with missing 'class'. Ensure it has 'cwlVersion', 'inputs', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'class' in CWL file"}),
        ("Generate an invalid CWL file with missing 'inputs'. Ensure it has 'cwlVersion', 'class', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'inputs' in CWL file"}),
        ("Generate an invalid CWL file with missing 'outputs'. Ensure it has 'cwlVersion', 'class', 'inputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'outputs' in CWL file"}),
        (f"Generate an invalid CWL file with unsupported 'cwlVersion' not in {VALID_CWL_VERSIONS}. Ensure it has 'class', 'inputs', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Unsupported CWL version"}),
        (f"Generate an invalid CWL file with unsupported 'class' not in {VALID_CWL_CLASSES}. Ensure it has 'cwlVersion', 'inputs', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Unsupported class"}),
        (f"Generate an invalid CWL file with incorrect 'inputs' type, only {FILE_TYPE} is allowed. Ensure it has 'cwlVersion', 'class', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Only 'File' type is supported for inputs"}),
        (f"Generate an invalid CWL file with incorrect 'outputs' type, only {FILE_TYPE} is allowed. Ensure it has 'cwlVersion', 'class', 'inputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Only 'File' type is supported for outputs"}),
        (f"Generate an invalid CWL file with unsupported requirement from {UNSUPPORTED_REQUIREMENTS}. Ensure it has 'cwlVersion', 'class', 'inputs', 'outputs', and 'baseCommand'.", 
         {"is_valid": False, "error": "Validation failed: Unsupported requirement"})
    ]

    for i, (prompt, expected_result) in enumerate(prompts):
        for j in range(num_files):
            try:
                cwl_content = generate_cwl_file(prompt)
                file_type = 'valid' if expected_result['is_valid'] else 'invalid'
                file_name = f'cwl_{file_type}_{i+1}_{j+1}.cwl'
                expected_result['file_type'] = file_type
                expected_result['file_name'] = file_name
                with open(os.path.join(output_dir, file_name), 'w') as f:
                    f.write(cwl_content)
                with open(os.path.join(output_dir, f'{file_name}.expected'), 'w') as f:
                    json.dump(expected_result, f)
                logging.info(f"Generated {file_name} and expected result")
            except Exception as e:
                logging.error(f"Failed to generate CWL file {i+1}_{j+1}: {e}")

if __name__ == "__main__":
    generate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 10)
