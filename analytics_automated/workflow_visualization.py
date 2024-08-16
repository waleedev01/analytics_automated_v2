import networkx as nx
import io
import base64
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import logging
from .models import Submission, Task, Result, Step # Adjust if Task and Submission are in different files

logger = logging.getLogger(__name__)

def extract_workflow_data(cwl_data): # not sure about implementation
    tasks = {}
    for step in cwl_data.get('steps', []):
        task_name = step.get('id', step.get('name', 'Unnamed Step'))
        inputs = step.get('in', [])
        outputs = step.get('out', [])
        requirements = step.get('requirements', [])

        tasks[task_name] = {
            'inputs': [inp if isinstance(inp, str) else inp.get('source') for inp in inputs],
            'outputs': outputs,
            'requires': [req.get('id') for req in requirements if 'id' in req]
        }
    return tasks


def plot_static_workflow2(tasks):
    try:
        G_static = nx.DiGraph()

        for task in tasks:
            task_name = task.name
            inputs = task.in_glob.split(',')  # Assuming `in_glob` is a comma-separated string of input filenames
            outputs = task.out_glob.split(',')  # Assuming `out_glob` is a comma-separated string of output filenames
            
            # Add nodes for inputs
            for inp in inputs:
                if inp:  # Check if input is not empty
                    G_static.add_node(inp, type='file', style='dotted', color='lightgreen')
                    G_static.add_edge(inp, task_name, color='gray', weight=1)
            
            # Add node for the task
            G_static.add_node(task_name, type='task', style='solid', color='skyblue')
            
            # Add nodes for outputs
            for out in outputs:
                if out:  # Check if output is not empty
                    G_static.add_node(out, type='file', style='dotted', color='lightcoral')
                    G_static.add_edge(task_name, out, color='black', weight=2)

        # Define the layout (e.g., shell layout for a circular distribution)
        pos = nx.shell_layout(G_static)

        plt.figure(figsize=(14, 12))

        # Draw nodes with custom styles
        task_nodes = [n for n in G_static.nodes if G_static.nodes[n]['type'] == 'task']
        input_nodes = [n for n in G_static.nodes if G_static.nodes[n]['type'] == 'file' and 'lightgreen' in G_static.nodes[n]['color']]
        output_nodes = [n for n in G_static.nodes if G_static.nodes[n]['type'] == 'file' and 'lightcoral' in G_static.nodes[n]['color']]

        nx.draw_networkx_nodes(G_static, pos, nodelist=task_nodes, node_shape='s', node_color='skyblue', node_size=3000, label='Tasks')
        nx.draw_networkx_nodes(G_static, pos, nodelist=input_nodes, node_shape='o', node_color='lightgreen', node_size=2500, label='Input Files')
        nx.draw_networkx_nodes(G_static, pos, nodelist=output_nodes, node_shape='o', node_color='lightcoral', node_size=2500, label='Output Files')

        # Draw edges with custom styles
        nx.draw_networkx_edges(G_static, pos, edge_color='gray', width=2)

        # Draw labels
        nx.draw_networkx_labels(G_static, pos, font_size=10, font_color='black')

        # Create custom legend
        legend_elements = [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='skyblue', markersize=15, label='Tasks'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=15, label='Input Files'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', markersize=15, label='Output Files')
        ]

        plt.legend(handles=legend_elements, loc='upper left', fontsize='large', frameon=True, shadow=True, borderpad=1.5, handletextpad=1.5, title="Legend", title_fontsize='large')

        plt.title('Static Workflow Visualization')

        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode plot to base64 string
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return img_data

    except Exception as e:
        logger.error(f'Error generating static workflow graph: {e}')
        raise


def plot_static_workflow_old(tasks):    # OLD FUNCTION
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

def plot_static_workflow(tasks):  # OLD FUNCTION
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


def plot_dynamic_workflow(tasks):  # OLD FUNCTION
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



def get_current_task_states2(submission_name):
    task_states = {}

    try:
        submission = Submission.objects.get(submission_name=submission_name)
        
        print(f"Submission found: {submission}")
        steps = Step.objects.filter(job=submission.job).order_by('ordering')
        print(f"Steps found: {steps}")
        results = Result.objects.filter(submission=submission)
        print(f"Results found: {results}")

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


def get_current_task_states(submission_id):   # OLD FUNCTION

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
