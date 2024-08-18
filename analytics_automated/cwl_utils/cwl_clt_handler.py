import logging
import json
from ..models import Backend, Task, Parameter, Environment, Configuration

logger = logging.getLogger(__name__)

# Define default values
DEFAULT_INCOMPLETE_OUTPUTS_BEHAVIOUR = 3
DEFAULT_CUSTOM_EXIT_STATUS = ""
DEFAULT_CUSTOM_EXIT_BEHAVIOUR = None
NOT_TASK_REQUIREMENTS = [
    {'class': 'ScatterFeatureRequirement'},
    {'class': 'SubworkflowFeatureRequirement'},
]
FORMAT_MAP = r"analytics_automated/cwl_utils/format_uri_mapping.json"
CONFIGURATION_CHOICES = {
    "Software": 0,
    "Dataset": 1,
    "Misc.": 2,
}

def load_format_mapping(file_path):
    """
    Loads a JSON format mapping from a file.

    Args:
        file_path (str): The path to the JSON file containing the format mapping.

    Returns:
        dict: A dictionary representing the format mapping. 
              Returns an empty dictionary if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            format_mapping = json.load(file)
        logging.info(f"Format mapping loaded successfully from {file_path}")
        return format_mapping
    except Exception as e:
        logging.error(f"Error loading format mapping from {file_path}: {e}")
        return {}


def handle_env_variable_req(requirements: list) -> dict[str, str]:
    """
    Extracts environment variable requirements from a CWL requirements list.

    Args:
        requirements (list): A list of CWL requirements.

    Returns:
        dict[str, str]: A dictionary of environment variables extracted from 
                        the EnvVarRequirement. 
                        Returns an empty dictionary if no environment variables are found or an error occurs.
    """
    logging.info(f"- Handling environment variable requirements -")
    try:
        for requirement in requirements:
            if requirement['class'] == 'EnvVarRequirement':
                logging.info(f"Found environment variable requirement: {requirement['envDef']}")
                return requirement['envDef']
    except Exception as e:
        logging.error(f"Error handling environment variable requirements: {e}")
    return {}


def handle_hint_software_hint(requirements: list) -> list:
    """
    Extracts software package requirements from a CWL hints list.

    Args:
        requirements (list): A list of CWL requirements or hints.

    Returns:
        list: A list of dictionaries representing software package configurations.
              Returns an empty list if no software packages are found or an error occurs.
    """
    logging.info(f"- Handling hint software package -")
    try:
        for requirement in requirements:
            if requirement['class'] == 'SoftwareRequirement':
                logging.info(f"Found software package requirement: {requirement['packages']}")
                s_packages = requirement['packages']
                if isinstance(s_packages, dict):
                    software_req_li = []
                    for p_name, p_attr in s_packages.items():
                        p_attr['name'] = p_name
                        p_attr['version'] = ",".join(p_attr.get('version', ""))
                        p_attr['type'] = "Software"
                        software_req_li.append(p_attr)
                    return software_req_li
                if isinstance(s_packages, list):
                    for p in s_packages:
                        p['name'] = p['package']
                        p['version'] = ",".join(p['version'])
                        p['type'] = "Software"
                    return s_packages
    except Exception as e:
        logging.error(f"Error handling software package requirements: {e}")
    return []


def handle_aa_custom_configuration(configrations: list) -> list:
    """
    Validates custom configurations in a list of CWL configurations.

    Args:
        configrations (list): A list of custom configuration dictionaries.

    Returns:
        list: The validated list of configurations.
    
    Raises:
        ValueError: If any configuration object is missing the 'name' field.
    """
    for config in configrations:
        if config.get('name') is None:
            raise ValueError("The name of Configuration object should not be empty!")
    return configrations


def parse_cwl_clt(cwl_data, name, workflow_req: list = None):
    """
    Parses a CWL CommandLineTool and extracts its components into a dictionary.

    Args:
        cwl_data (dict): The CWL data representing the CommandLineTool.
        name (str): The name of the task.
        workflow_req (list, optional): A list of workflow requirements, if any.

    Returns:
        dict: A dictionary containing the parsed components of the CommandLineTool.
    """
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

    logging.info(f"Parsing CWL command line tool: {name}")

    try:
        base_command_ini = cwl_data.get("baseCommand")
        if isinstance(base_command_ini, list):
            base_command = ' '.join(base_command_ini)
        else:
            base_command = base_command_ini
        del base_command_ini
    except Exception as e:
        logging.error(f"Error parsing CWL baseCommand: {e}")

    inputs = cwl_data.get("inputs", {})
    outputs = cwl_data.get("outputs", {})
    requirements = cwl_data.get("requirements", [])
    hints = cwl_data.get("hints", [])
    arguments = cwl_data.get("arguments", [])
    stdin = cwl_data.get("stdin")
    stdout = cwl_data.get("stdout")
    stderr = cwl_data.get("stderr")
    success_codes = cwl_data.get("successCodes", None)
    permanent_fail_codes = cwl_data.get("permanentFailCodes", None)
    label = cwl_data.get("label")
    doc = cwl_data.get("doc")
    shell_quote = cwl_data.get("shellQuote", False)
    ADD_INPUT_FIELD = True

    aa_task_config_li = []
    software_hints = []
    try:
        aa_task_config_li = handle_aa_custom_configuration(cwl_data.get("AAConfiguration", []))
        software_hints = handle_hint_software_hint(hints)
    except Exception as e:
        logging.error(f"Failed to parse custom configration fields for task {name}: {e}")
    
    if success_codes is not None:
        success_codes = ",".join(map(str, success_codes))
    if permanent_fail_codes is not None:
        permanent_fail_codes = ",".join(map(str, permanent_fail_codes))

    task = {
        "name": name,
        "base_command": base_command,
        "inputs": parse_cwl_inputs(inputs),
        "outputs": parse_cwl_outputs(outputs),
        "requirements": requirements,
        "environments": handle_env_variable_req(requirements),
        "hints": hints,
        "configurations": aa_task_config_li + software_hints,
        "arguments": arguments,
        "stdin": stdin,
        "stdout": stdout,
        "stderr": stderr,
        "success_codes": success_codes,
        "permanent_fail_codes": permanent_fail_codes,
        "label": label,
        "doc": doc,
        "shell_quote": shell_quote,
    }

    if stdout:
        task['stdout_glob'] = f".{stdout.split('.')[-1]}"
    else:
        task['stdout_glob'] = ""

    executable_parts = [base_command]

    try:
        for argument_item in arguments:
            if isinstance(argument_item, dict):
                argument_str = argument_item['valueFrom']
                argument_position = argument_item.get('position')
                argument_prefix = argument_item.get('prefix')
                argument_separate = argument_item.get('separate', True)
                if not argument_separate and argument_prefix:
                    argument_str = argument_prefix + argument_str
                elif argument_separate and argument_prefix:
                    argument_str = argument_prefix + " " + argument_str
                if argument_position:
                    executable_parts.insert(argument_position, argument_str)
                else:
                    executable_parts.append(argument_str)
            else:
                executable_parts.append(argument_item)
    except Exception as e:
        logging.error(f"Error processing arguments for task {name}: {e}")

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
                # Skip exit_code as input parameter
                if file_type == 'int' and input_data['name'] == 'exit_code':
                    in_globs.append("exit_code.txt")
                    continue
        
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
    del position_parameter, position_input

    try:
        executable_parts_str = [str(item) for item in executable_parts]
        executable = " ".join(executable_parts_str)
        in_glob = ",".join(in_globs)

        out_globs = []
        for idx, output_data in enumerate(task['outputs']):
            if output_data['type'] == 'File' and 'glob' in output_data['output_binding']:
                suffix = f".{output_data['output_binding'].get('glob').split('.')[-1]}"
                out_globs.append(suffix)
            # Include exit_code in out_glob as exit_code.txt
            elif output_data['type'] == 'int' and output_data['output_binding']['outputEval'] == "$(runtime.exitCode)":
                suffix = 'exit_code.txt'
                out_globs.append(suffix)
        out_glob = ",".join(out_globs)

        task['executable'] = executable
        task['in_glob'] = in_glob
        task['out_glob'] = out_glob
    except Exception as e:
        logging.error(f"Error finalizing task details for {name}: {e}")

    logging.info(f"Task parsed successfully: {task}")
    return task


def save_task_to_db(task_data, messages, cwl_content=None):
    """
    Saves a parsed CWL task to the database, updating if it already exists.

    Args:
        task_data (dict): The parsed task data to be saved.
        messages (list): A list to store messages about the saving process.
        cwl_content (str, optional): The CWL content of the task as a string.

    Returns:
        Task: The saved or updated Task object.
        None: If an error occurs during saving.
    """
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
            existing_task.custom_success_exit = task_data['success_codes']
            existing_task.custom_terminate_exit = task_data['permanent_fail_codes']
            existing_task.cwl_content = cwl_content  # store the entire CLT CWL
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
                stdout=task_data['stdout'],
                stdin=task_data['stdin'],
                arguments=task_data['arguments'],
                stderr=task_data['stderr'],
                custom_success_exit=task_data['success_codes'],
                custom_terminate_exit=task_data['permanent_fail_codes'],
                shell_quote=task_data['shell_quote'],
                cwl_content=cwl_content  # store the entire CLT CWL
            )
            message = f"Task saved successfully: {task_data['name']}"
            logging.info(message)

        for input_data in task_data['inputs']:
            try:
                # Skip inputs with File type
                file_type = input_data['type']
                if file_type == 'File':
                    continue

                # Skip exit_code as input parameter
                if file_type == 'int' and input_data['name'] == 'exit_code':
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

        for package in task_data['configurations']:
            try:
                c = Configuration.objects.create(
                    task=task,
                    type=CONFIGURATION_CHOICES.get(package.get('type'), 0),
                    name=package['name'],
                    version=package.get('version', None),
                    parameters=package.get('parameter', None)
                )
            except Exception as e:
                logging.error(f"Error saving configuration for task {task_data['name']}: {e}")

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
    """
    Checks if a task with the specified name already exists in the database.

    Args:
        task_name (str): The name of the task to check.
        messages (list): A list to store messages about the checking process.

    Returns:
        Task: The existing Task object if found.
        None: If the task is not found or an error occurs.
    """
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