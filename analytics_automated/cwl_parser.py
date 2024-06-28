import os
import yaml
import logging
from django.core.exceptions import ObjectDoesNotExist
from .models import Backend, Task, Parameter, Job, Step, Requirement
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


def read_cwl_file(cwl_path, filename, messages):
    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)

    validator = CWLSchemaValidator()
    is_valid, message = validator.validate_cwl(cwl_data)

    if not is_valid:
        logging.error(f"Validation Failed: {message}")
        messages.append(f"Validation Failed: {message}")
        return None

    cwl_class = cwl_data.get("class")

    if cwl_class == "Workflow":
        return parse_cwl_workflow(cwl_data, filename, messages)
    elif cwl_class == "CommandLineTool":
        task_data = parse_cwl_clt(cwl_data, filename)
        return save_task_to_db(task_data, messages)
    else:
        error_message = f"Unknown CWL class for file {cwl_path}"
        logging.error(error_message)
        messages.append(error_message)
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


def save_task_to_db(task_data, messages):
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
            message = f"Task already exists: {task_data['name']}"
            logging.info(message)
            messages.append(message)
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
        for requirement in task_data['requirements']:
            Requirement.objects.create(
                task=task,
                requirement_class=requirement['class'],
                payload=requirement)
        message = f"Task saved successfully: {task_data['name']}"
        logging.info(message)
        messages.append(message)
        return task
    except Exception as e:
        error_message = f"Failed to save task to database: {str(e)}"
        logging.error(error_message)
        messages.append(error_message)
        return None


def check_existing_task_in_db(task_name, messages):
    backend = Backend.objects.get(id=1)  # Assuming a default backend ID

    # Check if the task already exists
    existing_task = Task.objects.filter(
        name=task_name,
        backend=backend,
    ).first()

    if not existing_task:
        error_message = f"Task file not found: {task_name}"
        messages.append(error_message)
        return None

    return existing_task


def parse_cwl_workflow(cwl_data, filename, messages):
    steps = cwl_data.get("steps")
    step_source = {}
    task_arr = []
    task_details = []

    for step_name, step_detail in steps.items():
        task_input = step_detail.get("in")
        source_arr = []
        for input_detail in task_input.values():
            if isinstance(input_detail, dict):
                input_source = input_detail.get("source", None)
                if input_source:
                    source_arr.append(input_source.split('/')[0])
            elif isinstance(input_detail, list):
                for item in input_detail:
                    if "/" in item:
                        source_arr.append(item.split('/')[0])
            elif "/" in input_detail:
                source_arr.append(input_detail.split('/')[0])

        task_run = step_detail.get("run")

        if isinstance(task_run, dict) and task_run.get("class") == "CommandLineTool":
            logging.info(f"Parsing inline CommandLineTool for step: {step_name}")
            task_data = parse_cwl_clt(task_run, step_name)
            task = save_task_to_db(task_data, messages)
            if task:
                task_details.append(task_data)
                step_source[step_name] = set(source_arr)
        elif isinstance(task_run, str):
            if not task_run.endswith(".cwl"):
                task_run += ".cwl"

            task = check_existing_task_in_db(step_name, messages)
            if task:
                # task_details.append(task_detail) -> only for debugging
                step_source[step_name] = set(source_arr)
            else:
                error_message = f"Cancel job creation with name '{filename}' due to missing task file: {step_name}"
                logging.error(error_message)
                messages.append(error_message)
                return

        task_arr.append(step_name)

    order_mapping_initial = set_step_order({}, step_source)
    # Handle dependent that are defined before the dependencies step
    order_mapping_final = set_step_order(order_mapping_initial, step_source)

    logging.info(f"Order Mapping: {order_mapping_final}")
    logging.info(f"Task Sequence: {task_arr}")
    logging.info("Task Details:")
    logging.info(task_details)

    try:
        logging.info(f"Creating job for workflow: {filename}")
        job = Job.objects.create(name=filename, runnable=True)
    except IntegrityError:
        error_message = f"A job with name '{filename}' already exists."
        logging.error(error_message)
        messages.append(error_message)
        return None

    for task_name in task_arr:
        try:
            task = Task.objects.get(name=task_name)
            Step.objects.create(job=job, task=task, ordering=order_mapping_final[task_name])
        except ObjectDoesNotExist:
            error_message = f"Task {task_name} does not exist in the database"
            logging.error(error_message)
            messages.append(error_message)

    messages.append(f"Job '{filename}' created with tasks: {', '.join(task_arr)}")
    return order_mapping_final

def set_step_order(order_mapping, step_source):
    logging.info(f"Step Source: {step_source}")
    for step_name, source_list in step_source.items():
        if len(source_list) == 0:
            order_mapping[step_name] = 0
        else:
            order = 0
            for source in source_list:
                if source in order_mapping:
                    source_order = order_mapping[source]
                    if order <= source_order:
                        order = source_order + 1

            order_mapping[step_name] = order

    return order_mapping

def main(directory_path):
    workflow_files, clt_files = scan_cwl_directory(directory_path)
    for workflow_file, cwl_data in workflow_files.items():
        logging.info(f"Processing Workflow: {workflow_file}")
        parse_cwl_workflow(cwl_data, os.path.splitext(os.path.basename(workflow_file))[0])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main("analytics_automated/cwl_files")
