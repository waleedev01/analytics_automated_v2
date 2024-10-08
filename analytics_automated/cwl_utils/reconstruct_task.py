import os
import json
import logging
from ruamel.yaml import YAML
import io
from ..models import Task, Parameter, Environment

logger = logging.getLogger(__name__)

yaml = YAML()
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)
FORMAT_MAP = r"analytics_automated/cwl_utils/uri_format_mapping.json"


def python_type_to_cwl_type(py_type):
    """
    Maps Python types to their equivalent CWL types.

    Args:
        py_type (type): A Python type (e.g., str, int, float, bool).

    Returns:
        str: The corresponding CWL type as a string. Returns 'unknown' if the type is not mapped.
    """
    type_mapping = {
        str: "string",
        int: "int",
        float: "float",
        bool: "boolean",
        # list: "array",
        # dict: "record",
        # type(None): "null"
    }
    return type_mapping.get(py_type, "unknown")


def load_format_mapping(file_path):
    """
    Loads a JSON file containing format mappings for file types and returns it as a dictionary.

    Args:
        file_path (str): The path to the JSON file containing the format mappings.

    Returns:
        dict: A dictionary containing the format mappings. 
              If the file cannot be loaded, returns an empty dictionary and logs an error.
    """
    try:
        with open(file_path, 'r') as file:
            format_mapping = json.load(file)
        logging.info(f"Format mapping loaded successfully from {file_path}")
        return format_mapping
    except Exception as e:
        logging.error(f"Error loading format mapping from {file_path}: {e}")
        return {}


def parse_json_field(field):
    """
    Parses a string field containing JSON data into a Python object.

    Args:
        field (str or dict): The JSON field to parse. If already a dictionary, it is returned as is.

    Returns:
        dict: The parsed JSON data as a dictionary. 
              If the input is already a dictionary, it returns the input unchanged.
    """
    if isinstance(field, str):
        return json.loads(field)
    return field

def reconstruct_task_cwl(task, file_path):
    """
    Reconstructs a CommandLineTool CWL file for a given task and saves it to the specified file path.

    Args:
        task (Task): The task object from the database for which the CWL file is to be reconstructed.
        file_path (str): The file path where the reconstructed CWL file will be saved.

    Raises:
        Exception: If an error occurs during the reconstruction process, it's logged, and the function continues.

    Returns:
        None
    """
    logger.info(f"Reconstructing task: {task.name}")
    task_detail = {
        "cwlVersion": "v1.2",
        "class": "CommandLineTool",
        "baseCommand": task.executable.split(),
        "inputs": {},
        "outputs": {},
        "requirements": parse_json_field(task.requirements) or [],
    }

    # Conditionally add non-empty fields
    if task.hints:
        task_detail["hints"] = parse_json_field(task.hints)

    if task.success_codes:
        task_detail["successCodes"] = parse_json_field(task.success_codes)

    if task.temporary_fail_codes:
        task_detail["temporaryFailCodes"] = parse_json_field(task.temporary_fail_codes)

    if task.permanent_fail_codes:
        task_detail["permanentFailCodes"] = parse_json_field(task.permanent_fail_codes)

    if task.arguments:
        task_detail["arguments"] = parse_json_field(task.arguments)

    if task.stdin:
        task_detail["stdin"] = task.stdin

    if task.stdout:
        task_detail["stdout"] = task.stdout

    if task.stderr:
        task_detail["stderr"] = task.stderr

    if task.doc:
        task_detail["doc"] = task.doc

    if task.label:
        task_detail["label"] = task.label

    task_detail["shellQuote"] = task.shell_quote

    try:
        # Add input and output parameters
        # Update baseCommand
        positions_I: dict[str, int] = {}
        positions_P = []
        filtered_baseCommand = []
        for idx, item in enumerate(task_detail["baseCommand"]):
            if '$I' in item:
                positions_I[item] = idx
            elif '$P' in item:
                positions_P.append(idx)
            else:
                filtered_baseCommand.append(item)
        task_detail["baseCommand"] = filtered_baseCommand

        _add_input_parameters(task, task_detail, positions_P)
        _add_inputs(task, task_detail, positions_I)
    except Exception as e:
        logging.error(f"Error generating inputs for task {task.name}: {e}")

    _add_outputs(task, task_detail)

    # Save the CWL file
    try:
        with open(file_path, 'w') as file:
            yaml.dump(task_detail, file)
        logger.info(f"Task '{task.name}' saved as {file_path}")
    except Exception as e:
        logger.error(f"Failed to save task '{task.name}' as {file_path}: {str(e)}")


def _add_input_parameters(task, task_detail, positions_P):
    """
    Adds input parameters to the CWL task based on the associated task parameters.

    Args:
        task (Task): The task object containing the parameters to be added.
        task_detail (dict): The dictionary containing the CWL CommandLineTool details.
        positions_P (list[int]): The list of positions for input parameters in the base command.

    Returns:
        None
    """
    # Define inputs based on task parameters
    parameters = Parameter.objects.filter(task=task)
    idx = 0
    for p in parameters:
        p_input_binding = {
            "separate": p.spacing,
            "position": positions_P[idx],
        }
        idx += 1
        if not p.switchless:
            p_input_binding["prefix"] = p.flag

        p_attr_dict = {
            "inputBinding": p_input_binding,
        }
        if p.default:
            p_attr_dict["default"] = p.default
        if p.bool_valued:
            p_attr_dict["type"] = "boolean"
            p_attr_dict["default"] = True if p.default == "True" else False
        else:
            p_attr_dict["type"] = python_type_to_cwl_type(type(p.default))

        task_detail["inputs"][p.rest_alias] = p_attr_dict


def _add_inputs(task, task_detail, positions_I: dict[str, int]):
    """
    Adds input file references to the CWL task based on the in_globs field and their positions in the base command.

    Args:
        task (Task): The task object containing the input file globs.
        task_detail (dict): The dictionary containing the CWL CommandLineTool details.
        positions_I (dict[str, int]): A dictionary mapping input placeholders in the base command to their positions.

    Returns:
        None
    """
    # Define inputs based on in_globs and executable
    def map_format(format_uri, mapping):
        logging.info(f"Mapping format URI: {format_uri}")
        return mapping.get(format_uri, "Any")

    # Detect file format
    format_mapping = load_format_mapping(FORMAT_MAP)
    in_globs = task.in_glob.split(',')
    file_type = []
    for i, glob in enumerate(in_globs):
        if glob.strip():  # Skip empty globs
            file_type.append(map_format(glob, mapping=format_mapping))

    # Generate input content
    for input_str, input_p in positions_I.items():
        input_str_li = input_str.split('$')
        input_id = int(input_str_li[1][1:])
        input_binding = {}
        if input_str_li[0]:
            input_binding['prefix'] = input_str_li[0]
            input_binding['separate'] = False
        input_binding['position'] = input_p

        task_detail["inputs"][f"input_{input_id}"] = {
            "type": "File",
            "format": file_type[input_id-1],
            "inputBinding": input_binding,
        }

def _add_outputs(task, task_detail):
    """
    Adds output file references to the CWL task based on the out_globs field and other output-related fields.

    Args:
        task (Task): The task object containing the output file globs.
        task_detail (dict): The dictionary containing the CWL CommandLineTool details.

    Returns:
        None
    """
    # Define outputs based on task outputs
    out_globs = task.out_glob.split(',')
    if task.stdout:
        task_detail["outputs"]["stdout"] = {
            "type": "File",
            "outputBinding": {"glob": task.stdout}
        }
    for i, output in enumerate(out_globs):
        if output.strip():  # Skip empty outputs
            task_detail["outputs"][f"output_{i}"] = {
                "type": "File",
                "outputBinding": {"glob": "*" + output}
            }


def _add_environment(task, task_detail):
    """
    Adds environment variables to the CWL task based on the task's environment field.

    Args:
        task (Task): The task object containing the environment variables.
        task_detail (dict): The dictionary containing the CWL CommandLineTool details.

    Returns:
        None
    """
    # Add environment variables
    environments = task.environment.all()
    if environments.exists():
        task_detail["requirements"].append({
            "class": "EnvVarRequirement",
            "envDef": {env.env: env.value for env in environments}
        })
