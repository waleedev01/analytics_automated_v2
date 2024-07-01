import logging
from ..models import Backend, Task, Parameter

logger = logging.getLogger(__name__)

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
            "http://edamontology.org/format_3916": ".mtx",
            "http://edamontology.org/format_3310": ".ss",
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
    position_parameter = 1
    position_input = 1
    for idx, input_data in enumerate(task['inputs']):
        position = input_data['input_binding'].get('position')

        if position is None:
            # Handle no "position" key in input_binding
            position = len(executable_parts)
        
        type = input_data['type']
        if type != 'File':
            executable_parts.insert(position, f"$P{position_parameter}")
            position_parameter += 1
        else:
            executable_parts.insert(position, f"$I{position_input}")
            position_input += 1
            if 'format' in input_data:
                in_globs.append(map_format(input_data['format']))
            else:
                in_globs.append('.input')

    executable_parts_str = [str(item) for item in executable_parts]
    executable = " ".join(executable_parts_str)
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
            executable=task_data['executable'],
            requirements=task_data['requirements'],
        )
        for input_data in task_data['inputs']:

            # Skip inputs with File type
            type = input_data['type']
            if type == 'File':
                continue

            Parameter.objects.create(
                task=task,
                flag=input_data['name'],
                default=input_data.get('default'),
                bool_valued=(input_data['type'] == 'boolean'),
                rest_alias=input_data['name'],
                spacing=input_data['input_binding'].get('separate', True),
                switchless=input_data['input_binding'].get('prefix', None) is None
            )
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