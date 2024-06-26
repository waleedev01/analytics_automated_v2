import os
import yaml
import logging
from django.core.exceptions import ObjectDoesNotExist
from .models import Backend, Task, Parameter, Job, Step
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)
UNSUPPORTED_REQUIREMENTS = [
    'InlineJavascriptRequirement',
    'ResourceRequirement',
    'DockerRequirement',
]


class CWLSchemaValidator:
    def validate_cwl(self, cwl_data):
        try:
            if not cwl_data.get('cwlVersion'):
                raise ValueError("Missing 'cwlVersion' in CWL file")

            if not cwl_data.get('class'):
                raise ValueError("Missing 'class' in CWL file")

            if cwl_data.get('requirements'):
                for item in cwl_data.get('requirements'):
                    if item['class'] in UNSUPPORTED_REQUIREMENTS:
                        raise ValueError(f"Unsupported requirement: {item['class']}")

            return True, "CWL file is valid."
        except Exception as e:
            logging.error(f"Validation failed: {str(e)}")
            return False, f"Validation failed: {str(e)}"

def read_cwl_file(cwl_path, all_files):
    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)

    validator = CWLSchemaValidator()
    is_valid, message = validator.validate_cwl(cwl_data)

    if not is_valid:
        logging.error(f"Validation Failed: {message}")
        return None

    base_name = os.path.splitext(os.path.basename(cwl_path))[0]
    cwl_class = cwl_data.get("class")

    if cwl_class == "Workflow":
        return parse_cwl_workflow(cwl_data, base_name, all_files)
    elif cwl_class == "CommandLineTool":
        task_data = parse_cwl_clt(cwl_data, base_name)
        return save_task_to_db(task_data)
    else:
        logging.error(f"Unknown CWL class for file {cwl_path}")
        return None



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


def save_task_to_db(task_data):
    try:
        backend = Backend.objects.get(id=1)  # Assuming a default backend ID
        logging.info(f"Saving task to database: {task_data['name']}")

        # Check if the task already exists
        existing_task = Task.objects.filter(
            name=task_data['name'],
            backend=backend,
            executable=task_data['executable'],
            in_glob=task_data['in_glob'],
            out_glob=task_data['out_glob'],
            stdout_glob=task_data['stdout_glob'],
        ).first()

        if existing_task:
            logging.info(f"Task already exists: {task_data['name']}")
            return existing_task

        # Create a new task if it doesn't exist
        task = Task.objects.create(
            backend=backend,
            name=task_data['name'],
            description=task_data.get('doc'),
            in_glob=task_data['in_glob'],
            out_glob=task_data['out_glob'],
            stdout_glob=task_data['stdout_glob'],
            executable=task_data['executable']
        )
        for input_data in task_data['inputs']:
            Parameter.objects.create(
                task=task,
                flag=input_data['name'],
                default=input_data.get('default'),
                bool_valued=(input_data['type'] == 'boolean'),
                rest_alias=input_data['name'],
                spacing=input_data['input_binding'].get('separate', True),
                switchless=input_data['input_binding'].get('prefix', None) is None
            )
        logging.info(f"Task saved successfully: {task_data['name']}")
        return task
    except Exception as e:
        logging.error(f"Failed to save task to database: {str(e)}")
        return None



def parse_cwl_workflow(cwl_data, filename, all_files):
    try:
        logging.info(f"Creating job for workflow: {filename}")
        job = Job.objects.create(name=filename, runnable=True)
    except IntegrityError:
        logging.error(f"A job with name '{filename}' already exists.")
        return None

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

        if isinstance(task_run, dict) and task_run.get("class") == "CommandLineTool":
            logging.info(f"Parsing inline CommandLineTool for step: {step_name}")
            task_data = parse_cwl_clt(task_run, step_name)
            task = save_task_to_db(task_data)
            if task:
                task_details.append(task_data)
                step_source[step_name] = set(source_arr)
        elif isinstance(task_run, str):
            if not task_run.endswith(".cwl"):
                task_run += ".cwl"

            task_file_path = all_files.get(task_run)
            if task_file_path:
                try:
                    logging.info(f"Parsing task file: {task_file_path}")
                    with open(task_file_path, 'r') as task_file:
                        task_data = yaml.safe_load(task_file)
                        task_detail = parse_cwl_clt(task_data, step_name)
                        task = save_task_to_db(task_detail)
                        if task:
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

    for task_name in task_arr:
        try:
            task = Task.objects.get(name=task_name)
            Step.objects.create(job=job, task=task, ordering=order_mapping[task_name])
        except ObjectDoesNotExist:
            logging.error(f"Task {task_name} does not exist in the database")

    return order_mapping



def main(directory_path):
    workflow_files, clt_files = scan_cwl_directory(directory_path)
    for workflow_file, cwl_data in workflow_files.items():
        logging.info(f"Processing Workflow: {workflow_file}")
        parse_cwl_workflow(cwl_data, os.path.splitext(os.path.basename(workflow_file))[0])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main("analytics_automated/cwl_files")
