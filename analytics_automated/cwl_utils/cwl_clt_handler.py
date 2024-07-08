import logging
import re
import json
from ..models import Backend, Task, Parameter, Environment

logger = logging.getLogger(__name__)

# Define default values
DEFAULT_INCOMPLETE_OUTPUTS_BEHAVIOUR = 3
DEFAULT_CUSTOM_EXIT_STATUS = ""
DEFAULT_CUSTOM_EXIT_BEHAVIOUR = None
NOT_TASK_REQUIREMENTS = [
    {'class': 'ScatterFeatureRequirement'},
    {'class': 'SubworkflowFeatureRequirement'},
]
dynamic_input_file_pattern = r"input.[^_]+.basename"
FORMAT_MAP = r"analytics_automated/cwl_utils/format_uri_mapping.json"


def load_format_mapping(file_path):
    with open(file_path, 'r') as file:
        format_mapping = json.load(file)
    return format_mapping


def handle_env_variable_req(requirements: list) -> dict[str, str]:
    """
    Extract envVarRequirement as environment variable list
    """
    logging.info(f"Handling environment variable requirements: {requirements}")
    try:
        for requirement in requirements:
            if requirement['class'] == 'EnvVarRequirement':
                logging.info(f"Found environment variable requirement: {requirement['envDef']}")
                return requirement['envDef']
    except Exception as e:
        logging.error(f"Error handling environment variable requirements: {e}")
    return {}

def parse_cwl_clt(cwl_data, name, workflow_req: list = None):
    def map_format(format_uri, mapping):
        logging.info(f"Mapping format URI: {format_uri}")
        return mapping.get(format_uri, ".input")

    def parse_cwl_inputs(inputs: dict):
        logging.info(f"Parsing CWL inputs: {inputs}")
        parsed_inputs = []
        try:
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
        except Exception as e:
            logging.error(f"Error parsing CWL inputs: {e}")
        return parsed_inputs

    def parse_cwl_outputs(outputs: dict):
        logging.info(f"Parsing CWL outputs: {outputs}")
        parsed_outputs = []
        try:
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
        except Exception as e:
            logging.error(f"Error parsing CWL outputs: {e}")
        return parsed_outputs

    def dynamic_value_judge(input_li: list, max_out: int, value: str) -> str:
        try:
            if value == '$(runtime.tmpdir)':
                return "$TMP"
            # Check if the value matches the dynamic input file pattern
            if re.search(dynamic_input_file_pattern, value):
                parts = value.split('.')
                if len(parts) <= 2:
                    raise ValueError(f"Value '{value}' is not in the expected format 'inputs.input_field_name.basename'")
                input_name = parts[1]
                if not input_name in input_li:
                    raise ValueError(f"Unexpected input field {input_name}, should be in {input_li}")
                input_idx = input_li.index(input_name)
                return f"$I{input_idx}"
            # Handle Output
            if "$O" in value:
                if len(value) < 3 or not value[2].isdigit():
                    raise ValueError(f"Missing Output index in {value}")
                if value[2] > max_out:
                    raise IndexError(f"Only {max_out} in the task, index {value[2]} does not exist")
            return value
        except Exception as e:
            logging.error(f"Error generating dynamic output directory: {e}")

    logging.info(f"Parsing CWL command line tool: {name}")
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
    shell_quote = cwl_data.get("shellQuote", False)
    try:
        # custom field, Get values from cwl_data or use default values if not present
        incomplete_outputs_behaviour = cwl_data.get("AAIncompleteOutputsBehaviour",
                                                    DEFAULT_INCOMPLETE_OUTPUTS_BEHAVIOUR)
        custom_exit_status = cwl_data.get("AACustomExitStatus")
        custom_exit_behaviour = cwl_data.get("AACustomExitBehaviour")
        # Ensure custom_exit_behaviour is provided if custom_exit_status is present
        if custom_exit_status is not None and custom_exit_behaviour is None:
            raise ValueError(
                f"Missing CustomExitBehaviour for task {name}:"
                f" If you provide a custom exit status, you must provide a behaviour.")

        # If custom_exit_status is None, set it to the default value
        if custom_exit_status is None:
            custom_exit_status = DEFAULT_CUSTOM_EXIT_STATUS

    except Exception as e:
        logging.error(f"Failed to parse custom fields for task {name}: {e}")

    task = {
        "name": name,
        "base_command": base_command,
        "inputs": parse_cwl_inputs(inputs),
        "outputs": parse_cwl_outputs(outputs),
        "requirements": requirements,
        "environments": handle_env_variable_req(requirements),
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
        "shell_quote": shell_quote,
        "incomplete_outputs_behaviour": incomplete_outputs_behaviour,
        "custom_exit_status": custom_exit_status,
        "custom_exit_behaviour": custom_exit_behaviour,
    }

    if stdout:
        task['stdout_glob'] = f".{stdout.split('.')[-1]}"
    else:
        task['stdout_glob'] = ""

    if isinstance(base_command, list):
        executable_parts = base_command
    else:
        executable_parts = [base_command]

    max_out = len(task['outputs'])
    task_name_li = [t['name'] for t in task['inputs'] if t['type'] == 'File']
    for argument_item in arguments:
        if isinstance(argument_item, dict):
            argument = argument_item['valueFrom']
        else:
            argument = argument_item
        if '/' in argument:
            arg_li = argument.split('/')
            for i in range(len(arg_li)):
                arg_li[i] = dynamic_value_judge(input_li=task_name_li, max_out=max_out,
                                                value=arg_li[i])
            executable_parts.append('/'.join(arg_li))
        else:
            executable_parts.append(dynamic_value_judge(input_li=task_name_li, max_out=max_out,
                                                        value=argument))
    del max_out, task_name_li

    in_globs = []
    position_parameter = 1
    position_input = 1
    try:
        format_mapping = load_format_mapping(FORMAT_MAP)
        for idx, input_data in enumerate(task['inputs']):
            position = input_data['input_binding'].get('position')

            if position is None:
                # Handle no "position" key in input_binding
                position = len(executable_parts)

            file_type = input_data['type']
            if file_type != 'File':
                executable_parts.insert(position, f"$P{position_parameter}")
                position_parameter += 1
            else:
                insert_value = f"$I{position_input}"
                input_prefix = input_data['input_binding'].get('prefix')
                if input_prefix:
                    if not input_data['input_binding'].get('separate', True):
                        insert_value = f"{input_prefix}$I{position_input}"
                    else:
                        insert_value = f"{input_prefix} $I{position_input}"
                executable_parts.insert(position, insert_value)
                position_input += 1
                if 'format' in input_data:
                    file_format = map_format(input_data['format'], mapping=format_mapping)
                    in_globs.append(file_format)
                else:
                    in_globs.append('.input')
    except Exception as e:
        logging.error(f"Error processing inputs for task {name}: {e}")

    try:
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
        print(f"Generated executable command for {task['name']}", executable)
    except Exception as e:
        logging.error(f"Error finalizing task details for {name}: {e}")

    logging.info(f"Task parsed successfully: {task}")
    return task


def save_task_to_db(task_data, messages):
    try:
        backend = Backend.objects.get(id=1)  # Assuming a default backend ID
        logging.info(f"Saving task to database: {task_data['name']}")

        # Check if the task already exists
        existing_task = Task.objects.filter(
            name=task_data['name'],
            backend=backend,
        ).first()

        # Check if the environments is a dictionary or a list
        environments = task_data['environments']
        if isinstance(environments, dict):
            environment_items = environments.items()
        elif isinstance(environments, list):
            env_dict = {}
            for env in environments:
                if not isinstance(env, dict):
                    messages.append("Environment variables should be a dictionary")
                    return None
                env_dict[env.get('envName')] = env.get('envValue')
            environment_items = env_dict.items()
        else:
            messages.append("Environment variables should be a dictionary or a list")
            return None

        if existing_task:
            message = f"Found existing task with name: {existing_task}"
            logging.info(message)
            messages.append(message)

            existing_task.name = task_data['name']
            existing_task.description = task_data.get('doc')
            existing_task.in_glob = task_data['in_glob']
            existing_task.out_glob = task_data['out_glob']
            existing_task.stdout_glob = task_data['stdout_glob']
            existing_task.executable = task_data['executable']
            existing_task.requirements = task_data['requirements']
            existing_task.incomplete_outputs_behaviour = task_data['incomplete_outputs_behaviour']
            existing_task.custom_exit_status = task_data['custom_exit_status']
            existing_task.custom_exit_behaviour = task_data['custom_exit_behaviour']
            existing_task.save()

            existing_parameter = Parameter.objects.filter(task=existing_task)
            for param in existing_parameter:
                param.delete()
            existing_environment_var = Environment.objects.filter(task=existing_task)
            for env_var in existing_environment_var:
                env_var.delete()

            message = f"Task updated successfully: {task_data['name']}"
            logging.info(message)
            task = existing_task
        else:
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
                incomplete_outputs_behaviour=task_data['incomplete_outputs_behaviour'],
                custom_exit_status=task_data['custom_exit_status'],
                custom_exit_behaviour=task_data['custom_exit_behaviour'],
            )
            message = f"Task saved successfully: {task_data['name']}"
            logging.info(message)

        for input_data in task_data['inputs']:
            try:
                # Skip inputs with File type
                file_type = input_data['type']
                if file_type == 'File':
                    continue

                flag = input_data.get('input_binding').get('prefix')
                if flag is None:
                    flag = input_data['name']

                p = Parameter.objects.create(
                    task=task,
                    flag=flag,
                    default=input_data.get('default'),
                    bool_valued=(input_data['type'] == 'boolean'),
                    rest_alias=input_data['name'],
                    spacing=input_data['input_binding'].get('separate', True),
                    switchless=input_data['input_binding'].get('prefix', None) is None
                )
            except Exception as e:
                logging.error(f"Error saving parameter for task {task_data['name']}: {e}")

        for env_var_name, env_var_value in environment_items:
            try:
                # TODO: There are values that dynamic generated during CWL execution,
                #  should be handled during Celery execution. (For example: $(inputs.message))
                if '$' not in env_var_value:
                    Environment.objects.create(
                        task=task,
                        env=env_var_name,
                        value=env_var_value
                    )
            except Exception as e:
                logging.error(f"Error saving environment variable for task {task_data['name']}: {e}")

        message = f"Task saved successfully: {task_data['name']}"
        logging.info(message)
        messages.append(message)
        return task
    except Exception as e:
        error_message = f"Failed to save task to database: {e}"
        logging.error(error_message)
        messages.append(error_message)
        return None


def check_existing_task_in_db(task_name, messages):
    logging.info(f"Checking existing task in DB: {task_name}")
    try:
        backend = Backend.objects.get(id=1)  # Assuming a default backend ID

        # Check if the task already exists
        existing_task = Task.objects.filter(
            name=task_name,
            backend=backend,
        ).first()

        if not existing_task:
            error_message = f"Task file not found: {task_name}"
            logging.error(error_message)
            messages.append(error_message)
            return None

        return existing_task
    except Exception as e:
        error_message = f"Error checking existing task in DB: {e}"
        logging.error(error_message)
        messages.append(error_message)
        return None
