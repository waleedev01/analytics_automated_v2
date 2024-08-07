import networkx as nx
import io
import base64
import matplotlib.pyplot as plt
import logging
from .models import Submission, Task, Result, Step # Adjust if Task and Submission are in different files

logger = logging.getLogger(__name__)

def extract_workflow_data(cwl_data):
    tasks = {}
    for step in cwl_data.get('steps', []):
        task_name = step.get('id')
        inputs = step.get('in', [])
        outputs = step.get('out', [])
        requirements = [req['id'] for req in step.get('requirements', [])]
        tasks[task_name] = {
            'inputs': [inp['source'] for inp in inputs if 'source' in inp],
            'outputs': outputs,
            'requires': requirements
        }
    return tasks

def plot_static_workflow(tasks):
    G_static = nx.DiGraph()
    for task, details in tasks.items():
        G_static.add_node(task, type='task')
        for inp in details['inputs']:
            G_static.add_node(inp, type='file')
            G_static.add_edge(inp, task)
        for out in details['outputs']:
            G_static.add_node(out, type='file')
            G_static.add_edge(task, out)
        for req in details['requires']:
            G_static.add_edge(req, task)

    color_map = {
        'task': 'skyblue',
        'file': 'lightgreen'
    }
    node_colors = [color_map[G_static.nodes[node]['type']] for node in G_static.nodes]
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G_static, seed=42)
    nx.draw(G_static, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=10, font_color='black')
    plt.title("Static Workflow Visualization")
    plt.show()


def plot_static_workflow2(tasks):
    G_static = nx.DiGraph()
    for task, details in tasks.items():
        G_static.add_node(task, type='task')
        for inp in details['inputs']:
            G_static.add_node(inp, type='file')
            G_static.add_edge(inp, task)
        for out in details['outputs']:
            G_static.add_node(out, type='file')
            G_static.add_edge(task, out)
    
    pos = nx.spring_layout(G_static)
    plt.figure(figsize=(10, 7))
    nx.draw(G_static, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10, font_weight='bold')
    
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode plot to base64 string
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return img_data

def plot_dynamic_workflow(tasks):
    G_dynamic = nx.DiGraph()
    for task, details in tasks.items():
        G_dynamic.add_node(task, type='task', state=details['state'])
        for inp in details['inputs']:
            G_dynamic.add_node(inp, type='file')
            G_dynamic.add_edge(inp, task)
        for out in details['outputs']:
            G_dynamic.add_node(out, type='file')
            G_dynamic.add_edge(task, out)

    state_color_map = {
        'completed': 'green',
        'running': 'yellow',
        'pending': 'red',
        'failed': 'grey'
    }
    node_colors_dynamic = [state_color_map.get(G_dynamic.nodes[node].get('state', 'file'), 'lightgreen') for node in G_dynamic.nodes]
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G_dynamic, seed=42)
    nx.draw(G_dynamic, pos, with_labels=True, node_color=node_colors_dynamic, node_size=2000, font_size=10, font_color='black')
    plt.title("Dynamic Workflow Execution Visualization")
    plt.show()


def get_current_task_states(submission_id):

    task_states = {}

    try:
        # Fetch the submission
        submission = Submission.objects.get(pk=submission_id)

        # Fetch tasks associated with the submission
        tasks = Task.objects.filter(submission=submission)  # Assuming tasks are related to submissions

        for task in tasks:
            task_states[task.id] = {
                'inputs': task.inputs,  # Update with actual field/method for inputs
                'outputs': task.outputs,  # Update with actual field/method for outputs
                'state': task.status,  # Assuming `status` is the field representing task state
                'dependencies': [dep.id for dep in task.dependencies.all()]
            }
    except Submission.DoesNotExist:
        print(f"No submission found with ID {submission_id}")
    except Exception as e:
        print(f"An error occurred while fetching task states: {e}")

    return task_states


# EXAMPLE RUN

# tasks = extract_workflow_data(cwl_data)

# Static visualization (initial setup)

# plot_static_workflow(tasks)

# Dynamic visualization (during execution)

# submission_id = 1  Replace with the actual submission ID you want to visualize
# task_states = get_current_task_states(submission_id)   Function to fetch current states of tasks
# plot_dynamic_workflow(task_states)

def get_current_task_states2(submission_name):
    task_states = {}

    try:
        submission = Submission.objects.get(submission_name=submission_name)
        steps = Step.objects.filter(job=submission.job).order_by('ordering')
        results = Result.objects.filter(submission=submission)

        for step in steps:
            task = step.task
            result = results.filter(task=task).first()  # Assuming one result per task
            task_states[task.name] = {
                'task_name': task.name,
                'description': task.description,
                'inputs': task.in_glob,
                'outputs': task.out_glob,
                'state': result.message if result else 'pending',  # Use result message as state
                'dependencies': [s.task.name for s in Step.objects.filter(job=submission.job, ordering__lt=step.ordering)]
            }
    except Submission.DoesNotExist:
        logger.error(f"No submission found with name {submission_name}")
    except Exception as e:
        logger.error(f"An error occurred while fetching task states: {e}")

    return task_states