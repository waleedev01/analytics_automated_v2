import subprocess
import json
import os
import pandas as pd
import re

def sanitize_text(text):
    """Sanitize text by removing characters that are not allowed in Excel cells."""
    # Replace invalid characters with spaces
    sanitized = re.sub(r'[^\x20-\x7E]', ' ', text)  # Remove non-ASCII characters
    return sanitized


def run_cwl(cwl_file, input_file):
    # Ensure the CWL tool is installed and accessible
    cwltool_path = "cwltool"

    # Check if cwltool is available
    if subprocess.call(['which', cwltool_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        raise RuntimeError(f"{cwltool_path} is not installed or not in PATH.")

    # Construct the command to run the CWL file with cwltool
    command = [cwltool_path, cwl_file, input_file]

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Sanitize the output and error
    sanitized_stdout = sanitize_text(result.stdout)
    sanitized_stderr = sanitize_text(result.stderr)
    # Capture command output and error
    return {
        "cwl_file": cwl_file,
        "input_file": input_file,
        "stdout": sanitized_stdout,
        "stderr": sanitized_stderr,
        "returncode": result.returncode
    }

def main():
    # Define the paths to CWL files and input JSON files
    cwl_files = [
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/echo_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/cat_file_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/concat_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/conditional_workflow.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/env_var_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/multi_output_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/process_file_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/reverse_string_tool.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/simple_workflow.cwl',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/workflow_example.cwl',
        # Add paths to other CWL files as needed
    ]
    
    input_files = [
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/echo_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/cat_file_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/concat_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/conditional_workflow.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/env_var_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/multi_output_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/process_file_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/reverse_string_tool.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/simple_workflow.json',
        '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/input/workflow_example.json'
        # Add paths to corresponding input JSON files as needed
    ]

    # Ensure both lists have the same length
    if len(cwl_files) != len(input_files):
        raise ValueError("Mismatch between number of CWL files and input JSON files")

    results = []    

    # Run each CWL file with its corresponding input file
    for cwl_file, input_file in zip(cwl_files, input_files):
        print(f"Running CWL file: {cwl_file} with input: {input_file}")
        result = run_cwl(cwl_file, input_file)
        results.append(result)

    # Create a DataFrame from results
    df = pd.DataFrame(results)

    # Write the DataFrame to an Excel file
    output_excel = '/home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/tests/gen_cwl/cwl_results.xlsx'
    df.to_excel(output_excel, index=False)

    print(f"Results written to {output_excel}")

    
if __name__ == "__main__":
    main()



