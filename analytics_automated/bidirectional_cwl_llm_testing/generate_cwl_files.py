import os
import json
from openai import OpenAI
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='')

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
        logging.error(f"Error generating CWL file: {e}")
        raise

def generate_cwl_files(output_dir, num_files=10):
    os.makedirs(output_dir, exist_ok=True)
    
    prompts = [
        ("Generate a valid CWL file with cwlVersion, class, inputs, and outputs properly defined.", 
         {"is_valid": True, "error": None}),
        ("Generate an invalid CWL file with missing 'cwlVersion'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'cwlVersion' in CWL file"}),
        ("Generate an invalid CWL file with missing 'class'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'class' in CWL file"}),
        ("Generate an invalid CWL file with missing 'inputs'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'inputs' in CWL file"}),
        ("Generate an invalid CWL file with missing 'outputs'.", 
         {"is_valid": False, "error": "Validation failed: Missing 'outputs' in CWL file"}),
        ("Generate an invalid CWL file with unsupported 'cwlVersion'.", 
         {"is_valid": False, "error": "Validation failed: Unsupported CWL version: v1.3"}),
        ("Generate an invalid CWL file with unsupported 'class'.", 
         {"is_valid": False, "error": "Validation failed: Unsupported class: UnsupportedClass"}),
        ("Generate an invalid CWL file with incorrect 'inputs' type.", 
         {"is_valid": False, "error": "Validation failed: Please define inputs in CWL as dictionary"}),
        ("Generate an invalid CWL file with incorrect 'outputs' type.", 
         {"is_valid": False, "error": "Validation failed: Please define outputs in CWL as dictionary"}),
        ("Generate an invalid CWL file with invalid requirement.", 
         {"is_valid": False, "error": "Validation failed: Unsupported requirement: InlineJavascriptRequirement"})
    ]

    for i, (prompt, expected_result) in enumerate(prompts):
        try:
            cwl_content = generate_cwl_file(prompt)
            file_name = f'cwl_file_{i+1}.cwl'
            with open(os.path.join(output_dir, file_name), 'w') as f:
                f.write(cwl_content)
            with open(os.path.join(output_dir, f'{file_name}.expected'), 'w') as f:
                json.dump(expected_result, f)
            logging.info(f"Generated {file_name} and expected result")
        except Exception as e:
            logging.error(f"Failed to generate CWL file {i+1}: {e}")

if __name__ == "__main__":
    generate_cwl_files('analytics_automated/bidirectional_cwl_llm_testing/generated_cwl_files', 10)
