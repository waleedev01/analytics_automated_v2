import yaml

def read_cwl_file(cwl_path):
    with open(cwl_path, 'r') as cwl_file:
        cwl_data = yaml.safe_load(cwl_file)
    
    cwl_class = cwl_data.get("class")

    if cwl_class == "Workflow":
        return parse_cwl_workflow(cwl_data)
    elif cwl_class == "CommandLineTool":
        return parse_cwl_clt(cwl_data)
    else:
        #TODO: Add error handling
        return "Unknown CWL class"

def parse_cwl_clt(cwl_data):
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
