import os
import json
from openai import OpenAI
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI client with your API key
client = OpenAI(
    api_key='XXX',
)

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
    
    for i in range(num_files):
        prompt = "Generate a CWL file with the following characteristics:\n"
        if i % 2 == 0:
            prompt += "A valid CWL file for a CommandLineTool."
            expected_result = {"is_valid": True, "error": None}
        else:
            prompt += "An invalid CWL file with missing required fields."
            expected_result = {"is_valid": False, "error": "Expected error message"}

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
    generate_cwl_files('analytics_automated/llm_testing/generated_cwl_files', 10)
