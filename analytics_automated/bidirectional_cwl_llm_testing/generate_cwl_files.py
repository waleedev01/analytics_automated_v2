import os
import json
import logging
from openai import OpenAI
import re

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='')

# Define variables for prompts
VALID_CWL_VERSIONS = ['v1.0', 'v1.1', 'v1.2']
VALID_CWL_CLASSES = ['CommandLineTool', 'Workflow']
SUPPORTED_REQUIREMENTS = [
    'ShellCommandRequirement',
    'EnvVarRequirement',
    'InitialWorkDirRequirement',
    'SoftwareRequirement',
    'InlineJavascriptRequirement'
]

def generate_cwl_file(prompt):
    """
    Generate a CWL file content based on a given prompt using the OpenAI API.

    Args:
        prompt (str): The prompt to send to the OpenAI API to generate CWL content.

    Returns:
        str: The generated CWL content as a string.

    Raises:
        Exception: If there is an error generating the CWL file.
    """
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
        cwl_content = response.choices[0].message.content.strip()
        # Remove the expected result if it is included in the file content
        if "This CWL file is" in cwl_content:
            cwl_content = cwl_content.split("This CWL file is")[0].strip()
        return cwl_content
    except Exception as e:
        logger.error(f"Error generating CWL file: {e}")
        raise

def extract_clt_filenames(workflow_content):
    """
    Extract filenames of CommandLineTool files from the given workflow content.

    Args:
        workflow_content (str): The content of the CWL workflow file.

    Returns:
        list: A list of filenames of CommandLineTool files referenced in the workflow.
    """
    # Extract the filenames of the CommandLineTool files from the workflow content
    pattern = r'run:\s*(\S+)'
    matches = re.findall(pattern, workflow_content)
    return matches

def generate_clt_files(clt_filenames, output_dir):
    """
    Generate and save CWL CommandLineTool files based on the given filenames.

    Args:
        clt_filenames (list): A list of filenames for CommandLineTool files.
        output_dir (str): The directory where the generated CLT files will be saved.

    Returns:
        None
    """
    for clt_filename in clt_filenames:
        prompt = f"Generate a valid CWL CommandLineTool file named {clt_filename} with a baseCommand, inputs, and outputs properly defined."
        try:
            clt_content = generate_cwl_file(prompt)
            with open(os.path.join(output_dir, clt_filename), 'w') as f:
                f.write(clt_content)
            logging.info(f"Generated CLT file: {clt_filename}")
        except Exception as e:
            logging.error(f"Failed to generate CLT file {clt_filename}: {e}")

def generate_cwl_files(output_dir, num_files):
    """
    Generate multiple CWL files of different types (valid and invalid) and save them to the specified directory.

    Args:
        output_dir (str): The directory where the generated CWL files will be saved.
        num_files (int): The number of files to generate for each prompt type.

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)

    prompts = [
        (f"Generate a valid CWL file with cwlVersion from {VALID_CWL_VERSIONS}, class from {VALID_CWL_CLASSES}, baseCommand, inputs, and outputs properly defined as dictionaries. "
         f"Ensure the class is CommandLineTool, includes a baseCommand, and supports any type for inputs and outputs.", 
         {"is_valid": True, "error": "CWL file is valid."}),
        (f"Generate a valid CWL file with cwlVersion from {VALID_CWL_VERSIONS}, class from {VALID_CWL_CLASSES}, baseCommand, inputs, and outputs properly defined as dictionaries. "
         f"Ensure the class is Workflow, includes steps defined as dictionaries, and supports any type for inputs and outputs. "
         f"Also, include any necessary CommandLineTool files referenced within the workflow.", 
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
        (f"Generate an invalid CWL file with unsupported requirement in the 'requirements' field. Use a requirement that is not in {SUPPORTED_REQUIREMENTS}. Ensure it has 'cwlVersion', 'class', 'inputs', 'outputs', and 'baseCommand'.", 
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

                if expected_result['is_valid'] and 'Workflow' in cwl_content:
                    # Extract CLT filenames and generate CLT files
                    clt_filenames = extract_clt_filenames(cwl_content)
                    generate_clt_files(clt_filenames, output_dir)
                    
            except Exception as e:
                logging.error(f"Failed to generate CWL file {i+1}_{j+1}: {e}")

if __name__ == "__main__":
    generate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files_valid', 10)
