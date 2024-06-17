import yaml
import pprint


def read_cwl_file(cwl_path):
    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)
    
    cwl_class = cwl_data.get("class")

    if cwl_class == "Workflow":
        # print(f'[Detected] Workflow {cwl_file}')
        return parse_cwl_workflow(cwl_data)
    elif cwl_class == "CommandLineTool":
        # print(f'[Detected] CommandLineTool {cwl_file} ')
        return parse_cwl_clt(cwl_data)
    else:
        #TODO: Add error handling
        return "Unknown CWL class"


def parse_cwl_clt(cwl_data):
    def parse_cwl_inputs(inputs: dict):
        parsed_inputs = []
        for input_name, input_data in inputs.items():
            input_type = input_data.get("type")
            input_binding = input_data.get("inpuutBinding", {})
            parsed_input = {
                "name": input_name,
                "type": input_type,
                "input_binding": input_binding
            }
            parsed_inputs.append(parsed_input)
        return parsed_inputs

    def parse_cwl_outputs(outputs: dict):
        parsed_outputs = []
        for output_name, output_data in outputs.items():
            output_type = output_data.get("type")
            output_binding = output_data.get("outputBinding", {})
            glob = output_binding.get("glob")

            # Example: Mapping CWL output to AA output format
            parsed_output = {
                "name": output_name,
                "type": output_type,
                "output_binding": output_binding
            }

            # Check if there is a glob pattern defined
            if glob:
                parsed_output["out_glob"] = glob

            parsed_outputs.append(parsed_output)

        return parsed_outputs

    base_command = cwl_data.get("baseCommand")
    arguments = cwl_data.get("arguments", [])
    inputs = cwl_data.get("inputs", [])
    outpus = cwl_data.get("outputs", [])

    task = {
        "base_command": base_command,
        "arguments": arguments,
        "inputs": parse_cwl_inputs(inputs),
        "outputs": parse_cwl_outputs(outpus)
    }
    print(task)
    return None


def parse_cwl_workflow(cwl_data):
    inputs = cwl_data.get("inputs")
    outputs = cwl_data.get("outputs")
    steps = cwl_data.get("steps")

    for step_name, step_detail in steps.items():
        task_name = step_name
        task_run = step_detail.get("run")
        task_in = step_detail.get("in")
        task_out = step_detail.get("out")
