import yaml
import cwlgen

class Job:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Task:
    def __init__(self, name, description, executable, in_glob, out_glob, stdout_glob, stderr_glob=None):
        self.name = name
        self.description = description
        self.executable = executable
        self.in_glob = in_glob
        self.out_glob = out_glob
        self.stdout_glob = stdout_glob
        self.stderr_glob = stderr_glob

class Step:
    def __init__(self, job, task, ordering):
        self.job = job
        self.task = task
        self.ordering = ordering

class Parameter:
    def __init__(self, flag, default, param_type='string', input_binding=None):
        self.flag = flag
        self.default = default
        self.param_type = param_type
        self.input_binding = input_binding

class Environment:
    def __init__(self, env, value):
        self.env = env
        self.value = value

class Configuration:
    def __init__(self, task, type, name, parameters, version):
        self.task = task
        self.type = type
        self.name = name
        self.parameters = parameters
        self.version = version

def fetch_mock_job_data(job_id):
    job = Job(id=job_id, name="Example Job")
    tasks = [
        Task(
            name="Task 1",
            description="Description for Task 1",
            executable="echo",
            in_glob="*.txt",
            out_glob="output.txt",
            stdout_glob="stdout.log",
            stderr_glob="stderr.log"
        ),
        Task(
            name="Task 2",
            description="Description for Task 2",
            executable="cat",
            in_glob="output.txt",
            out_glob="final_output.txt",
            stdout_glob="stdout.log",
            stderr_glob="stderr.log"
        )
    ]
    
    steps = [
        Step(job=job, task=tasks[0], ordering=1),
        Step(job=job, task=tasks[1], ordering=2)
    ]
    
    job_data = {
        'name': job.name,
        'steps': []
    }
    
    for step in steps:
        task = step.task
        if task.name == "Task 1":
            task_data = {
                'name': task.name,
                'description': task.description,
                'executable': task.executable,
                'inputs': [{'id': 'message', 'type': 'string', 'default': 'Hello World', 'input_binding': {'position': 1}}],
                'stdout_glob': task.stdout_glob,
                'stderr_glob': task.stderr_glob,
                'parameters': [vars(Parameter(flag="--param", default="value"))],
                'environment': [vars(Environment(env="ENV_VAR", value="value"))],
                'configurations': [vars(Configuration(task=task, type="Software", name="Config1", parameters="param1", version="1.0"))]
            }
        elif task.name == "Task 2":
            task_data = {
                'name': task.name,
                'description': task.description,
                'executable': task.executable,
                'inputs': [{'id': 'input_file', 'type': 'File', 'input_binding': {'position': 1}}],
                'stdout_glob': task.stdout_glob,
                'stderr_glob': task.stderr_glob,
                'parameters': [vars(Parameter(flag="--param", default="value"))],
                'environment': [vars(Environment(env="ENV_VAR", value="value"))],
                'configurations': [vars(Configuration(task=task, type="Software", name="Config2", parameters="param2", version="2.0"))]
            }
        job_data['steps'].append(task_data)
    
    return job_data

def generate_cwl_file(job_data, file_path):
    workflow = cwlgen.Workflow()
    workflow.label = job_data['name']
    
    for i, step in enumerate(job_data['steps']):
        step_id = f"step_{i+1}"
        tool = cwlgen.CommandLineTool(base_command=step['executable'])
        tool.id = step_id
        
        for param in step['parameters']:
            tool.inputs.append(
                cwlgen.CommandInputParameter(
                    param['flag'],
                    param_type=param['param_type'],
                    default=param['default']
                )
            )
        
        for input in step['inputs']:
            tool.inputs.append(
                cwlgen.CommandInputParameter(
                    input['id'],
                    param_type=input['type'],
                    default=input.get('default'),
                    input_binding=input.get('input_binding')
                )
            )
        
        for env in step['environment']:
            tool.requirements.append(
                cwlgen.EnvVarRequirement({env['env']: env['value']})
            )
        
        tool.stdout = step['stdout_glob'] or 'stdout.log'
        tool.stderr = step.get('stderr_glob') or 'stderr.log'
        
        workflow_step = cwlgen.WorkflowStep(
            step_id=step_id,
            run=tool
        )
        
        workflow_step.out = ["output"]
        if i > 0:
            workflow_step.in_ = {"input_file": f"step_{i}/output"}
        workflow.steps.append(workflow_step)
    
    workflow.outputs.append(
        cwlgen.WorkflowOutputParameter(
            param_id="final_output",
            param_type="File",
            output_source=f"step_{len(job_data['steps'])}/output"
        )
    )
    
    workflow.export(file_path)

if __name__ == "__main__":
    job_id = 1
    job_data = fetch_mock_job_data(job_id)
    generate_cwl_file(job_data, 'workflow.cwl')
