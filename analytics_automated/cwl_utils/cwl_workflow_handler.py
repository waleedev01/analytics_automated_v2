import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from ..models import Job, Step, Task, Environment
from .cwl_clt_handler import parse_cwl_clt, save_task_to_db, check_existing_task_in_db, handle_env_variable_req

logger = logging.getLogger(__name__)

def parse_cwl_workflow(cwl_data, filename, messages):
    logging.info(f"Parsing CWL workflow: {filename}")
    steps = cwl_data.get("steps")
    step_source = {}
    task_arr = []
    task_details = []
    workflow_req = cwl_data.get("requirements", [])

    for step_name, step_detail in steps.items():
        logging.info(f"Processing step: {step_name}")
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

        try:
            if isinstance(task_run, dict) and task_run.get("class") == "CommandLineTool":
                logging.info(f"Parsing inline CommandLineTool for step: {step_name}")
                task_data = parse_cwl_clt(task_run, step_name)
                task = save_task_to_db(task_data, messages)
                if task:
                    task_details.append(task_data)
                    step_source[step_name] = set(source_arr)
                else:
                    error_message = f"Cancel job creation with name '{filename}' due to failure when creating task file: {step_name}"
                    logging.error(error_message)
                    messages.append(error_message)
                    return
            elif isinstance(task_run, str):
                if not task_run.endswith(".cwl"):
                    task_run += ".cwl"
                    
                task_name = task_run.split(".cwl")[0]

                task = check_existing_task_in_db(task_name, messages)
                if task:
                    step_source[task_name] = set(source_arr)
                else:
                    error_message = f"Cancel job creation with name '{filename}' due to missing task file: {task_name}"
                    logging.error(error_message)
                    messages.append(error_message)
                    return
        except Exception as e:
            error_message = f"Error processing task run for step {step_name}: {e}"
            logging.error(error_message)
            messages.append(error_message)
            return

        task_arr.append(task.name)

    # Check for circular dependencies
    for step_name, source_list in step_source.items():
        for item in source_list:
            if step_name in step_source.get(item, set()):
                error_message = f"Cancel job creation with name '{filename}' due to circular dependency in step: {step_name}"
                logging.error(error_message)
                messages.append(error_message)
                return

    try:
        order_mapping_initial = set_step_order({}, step_source)
        # Handle dependents that are defined before the dependencies step
        order_mapping_final = set_step_order(order_mapping_initial, step_source)
    except Exception as e:
        error_message = f"Error setting step order for workflow {filename}: {e}"
        logging.error(error_message)
        messages.append(error_message)
        return

    logging.info(f"Order Mapping: {order_mapping_final}")
    logging.info(f"Task Sequence: {task_arr}")
    logging.info("Task Details:")
    logging.info(task_details)

    logging.info(f"Creating job for workflow: {filename}")

    cwl_version = cwl_data.get("cwlVersion")
    requirements = cwl_data.get("requirements")

    try:
        # Check if the job already exists
        existing_job = Job.objects.filter(name=filename).first()

        if existing_job:
            message = f"Found existing job with name: {filename}"
            logging.info(message)
            messages.append(message)

            existing_job.name = filename
            existing_job.cwl_version = cwl_version
            existing_job.requirements = requirements
            existing_job.save()

            existing_step = Step.objects.filter(job=existing_job)
            for step in existing_step:
                step.delete()

            job = existing_job
            keyword = "updated"
        else:
            job = Job.objects.create(
                name=filename, 
                runnable=True,
                cwl_version=cwl_version,
                requirements=requirements)
            keyword = "created"

        for task_name in task_arr:
            try:
                # Create steps for the job
                task = Task.objects.get(name=task_name)
                Step.objects.create(job=job, task=task, ordering=order_mapping_final[task_name])

                # Create inherited workflow environment variables for the task
                if workflow_req:
                    curr_env = Environment.objects.filter(task=task)
                    env_dict = {}
                    for env in curr_env:
                        env_dict[env.env] = env.value

                    inherited_req = filter_workflow_req(workflow_req)
                    inherited_env_var_li = handle_env_variable_req(inherited_req)

                    for key, value in inherited_env_var_li.items():
                        if key not in env_dict:
                            Environment.objects.create(task=task, env=key, value=value)
            except ObjectDoesNotExist:
                error_message = f"Task {task_name} does not exist in the database"
                logging.error(error_message)
                messages.append(error_message)
            except IntegrityError as e:
                error_message = f"Integrity error when creating step for task {task_name}: {e}"
                logging.error(error_message)
                messages.append(error_message)
    except Exception as e:
        error_message = f"Error creating or updating job {filename}: {e}"
        logging.error(error_message)
        messages.append(error_message)
        return None

    messages.append(f"Job '{filename}' {keyword} with tasks: {', '.join(task_arr)}")
    logging.info(f"Job '{filename}' {keyword} with tasks: {', '.join(task_arr)}")
    return job

def set_step_order(order_mapping, step_source):
    logging.info(f"Setting step order. Step Source: {step_source}")
    try:
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
    except Exception as e:
        logging.error(f"Error setting step order: {e}")

    return order_mapping

def filter_workflow_req(requirements):
    """
    Remove requirement should not be inherited by task
    """
    logging.info(f"Filtering workflow requirements: {requirements}")
    try:
        return list(filter(lambda req: req['class'] not in ['ScatterFeatureRequirement',
                                                            'SubworkflowFeatureRequirement'],
                           requirements))
    except Exception as e:
        logging.error(f"Error filtering workflow requirements: {e}")
        return []
