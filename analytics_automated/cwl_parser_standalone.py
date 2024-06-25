import os
import yaml
import logging

logging.basicConfig(filename='cwl_parser.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

class CWLSchemaValidator:
    def validate_cwl(self, cwl_path):
        try:
            with open(cwl_path, 'r') as file:
                cwl_data = yaml.safe_load(file)

            if not cwl_data.get('cwlVersion'):
                raise ValueError("Missing 'cwlVersion' in CWL file")

            if not cwl_data.get('class'):
                raise ValueError("Missing 'class' in CWL file")

            return True, "CWL file is valid."
        except Exception as e:
            logging.error(f"Validation failed: {str(e)}")
            return False, f"Validation failed: {str(e)}"

def scan_cwl_directory(directory_path):
    cwl_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.cwl')]
    workflow_files = {}
    clt_files = []

    for cwl_file in cwl_files:
        try:
            with open(cwl_file, 'r') as file:
                cwl_data = yaml.safe_load(file)
                cwl_class = cwl_data.get("class")

                if cwl_class == "Workflow":
                    workflow_files[cwl_file] = cwl_data
                elif cwl_class == "CommandLineTool":
                    clt_files.append(cwl_file)
        except Exception as e:
            logging.error(f"Failed to read {cwl_file}: {str(e)}")

    return workflow_files, clt_files

def read_cwl_file(cwl_path):
    validator = CWLSchemaValidator()
    is_valid, message = validator.validate_cwl(cwl_path)
    
    if not is_valid:
        logging.error(f"Validation Failed: {message}")
        return None

    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)
    base_name = os.path.splitext(os.path.basename(cwl_path))[0]
    cwl_class = cwl_data.get("class")

    if cwl_class == "Workflow":
        return parse_cwl_workflow(cwl_data, base_name)
    elif cwl_class == "CommandLineTool":
        return parse_cwl_clt(cwl_data, base_name)
    else:
        logging.error(f"Unknown CWL class for file {cwl_path}")
        return "Unknown CWL class"

def parse_cwl_clt(cwl_data, name):
    def map_format(format_uri):
        EDAM_FORMAT_MAPPING = {
            "http://edamontology.org/format_1929": ".fasta",
            "http://edamontology.org/format_2330": ".fasta",
            "http://edamontology.org/format_1930": ".fastq",
            "http://edamontology.org/format_2572": ".bam",
            "http://edamontology.org/format_3016": ".vcf",
            "http://edamontology.org/format_3752": ".csv",
            "http://edamontology.org/format_3464": ".json",
        }
        return EDAM_FORMAT_MAPPING.get(format_uri, ".input")

    def parse_cwl_inputs(inputs: dict):
        parsed_inputs = []
        for input_name, input_data in inputs.items():
            input_type = input_data.get("type")
            input_format = input_data.get("format")
            input_binding = input_data.get("inputBinding", {})
            default_value = input_data.get("default")
            secondary_files = input_data.get("secondaryFiles", [])
            parsed_input = {
                "name": input_name,
                "type": input_type,
                "format": input_format,
                "default": default_value,
                "input_binding": input_binding,
                "secondary_files": secondary_files
            }
            parsed_inputs.append(parsed_input)
        return parsed_inputs

    def parse_cwl_outputs(outputs: dict):
        parsed_outputs = []
        for output_name, output_data in outputs.items():
            output_type = output_data.get("type")
            output_binding = output_data.get("outputBinding", {})
            secondary_files = output_data.get("secondaryFiles", [])
            parsed_output = {
                "name": output_name,
                "type": output_type,
                "output_binding": output_binding,
                "secondary_files": secondary_files
            }
            parsed_outputs.append(parsed_output)
        return parsed_outputs

    base_command = cwl_data.get("baseCommand")
    inputs = cwl_data.get("inputs", [])
    outputs = cwl_data.get("outputs", [])
    requirements = cwl_data.get("requirements", [])
    hints = cwl_data.get("hints", [])
    arguments = cwl_data.get("arguments", [])
    stdin = cwl_data.get("stdin")
    stdout = cwl_data.get("stdout")
    stderr = cwl_data.get("stderr")
    success_codes = cwl_data.get("successCodes", [])
    temporary_fail_codes = cwl_data.get("temporaryFailCodes", [])
    permanent_fail_codes = cwl_data.get("permanentFailCodes", [])
    label = cwl_data.get("label")
    doc = cwl_data.get("doc")
    initial_work_dir = cwl_data.get("initialWorkDir")
    shell_quote = cwl_data.get("shellQuote", False)

    task = {
        "name": name,
        "base_command": base_command,
        "inputs": parse_cwl_inputs(inputs),
        "outputs": parse_cwl_outputs(outputs),
        "requirements": requirements,
        "hints": hints,
        "arguments": arguments,
        "stdin": stdin,
        "stdout": stdout,
        "stderr": stderr,
        "success_codes": success_codes,
        "temporary_fail_codes": temporary_fail_codes,
        "permanent_fail_codes": permanent_fail_codes,
        "label": label,
        "doc": doc,
        "initial_work_dir": initial_work_dir,
        "shell_quote": shell_quote,
    }

    if stdout:
        task['stdout_glob'] = f".{stdout.split('.')[-1]}"
    else:
        task['stdout_glob'] = ""

    if isinstance(base_command, list):
        executable_parts = base_command
    else:
        executable_parts = [base_command]

    in_globs = []
    for idx, input_data in enumerate(task['inputs']):
        input_position = 1
        position = input_data['input_binding'].get('position')
        type = input_data['type']
        if type != 'File':
            executable_parts.append(f"$P{position}")
        else:
            executable_parts.append(f"$I{input_position}")
            input_position += 1
            if 'format' in input_data:
                in_globs.append(map_format(input_data['format']))
            else:
                in_globs.append('.input')

    executable = " ".join(executable_parts)
    in_glob = ",".join(in_globs)

    out_globs = []
    for idx, output_data in enumerate(task['outputs']):
        if output_data['type'] == 'File' and 'glob' in output_data['output_binding']:
            suffix = f".{output_data['output_binding'].get('glob').split('.')[-1]}"
            out_globs.append(suffix)
    out_glob = ",".join(out_globs)

    task['executable'] = executable
    task['in_glob'] = in_glob
    task['out_glob'] = out_glob

    return task

def parse_cwl_workflow(cwl_data, filename):
    steps = cwl_data.get("steps")
    step_source = {}
    task_arr = []
    task_details = []
    for step_name, step_detail in steps.items():
        task_input = step_detail.get("in")
        source_arr = []
        for input_name, input_detail in task_input.items():
            if isinstance(input_detail, dict):
                input_source = input_detail.get("source", None)
                if input_source:
                    source_arr.append(input_source.split('/')[0])

        task_run = step_detail.get("run")

        if not task_run.endswith(".cwl"):
            task_run += ".cwl"

        task_file_path = os.path.join("cwl_files", task_run)

        if os.path.exists(task_file_path):
            try:
                with open(task_file_path, 'r') as task_file:
                    task_data = yaml.safe_load(task_file)
                    task_detail = parse_cwl_clt(task_data, step_name)
                    task_details.append(task_detail)
                    step_source[step_name] = set(source_arr)
            except Exception as e:
                logging.error(f"Error parsing task {task_run}: {str(e)}")
        
        task_arr.append(step_name)

    order_mapping = {}
    order = 0

    for step_name in step_source:
        if step_name not in order_mapping:
            order_mapping[step_name] = order
            order += 1
        dependencies = step_source[step_name]
        for dependency in dependencies:
            if dependency not in order_mapping:
                order_mapping[dependency] = order
                order += 1

    logging.info(f"Order Mapping: {order_mapping}")
    logging.info(f"Task Sequence: {task_arr}")
    logging.info("Task Details:")
    logging.info(task_details)
    return order_mapping

def main(directory_path):
    workflow_files, clt_files = scan_cwl_directory(directory_path)
    for workflow_file, cwl_data in workflow_files.items():
        logging.info(f"Processing Workflow: {workflow_file}")
        parse_cwl_workflow(cwl_data, os.path.splitext(os.path.basename(workflow_file))[0])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main("cwl_files")