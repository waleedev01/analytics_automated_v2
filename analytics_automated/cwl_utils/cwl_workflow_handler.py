import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from ..models import Job, Step, Task
from .cwl_clt_handler import parse_cwl_clt, save_task_to_db, check_existing_task_in_db

logger = logging.getLogger(__name__)

def parse_cwl_workflow(cwl_data, filename, messages):
    steps = cwl_data.get("steps")
    step_source = {}
    task_arr = []
    task_details = []

    for step_name, step_detail in steps.items():
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

            task = check_existing_task_in_db(step_name, messages)
            if task:
                # task_details.append(task_detail) -> only for debugging
                step_source[step_name] = set(source_arr)
            else:
                error_message = f"Cancel job creation with name '{filename}' due to missing task file: {step_name}"
                logging.error(error_message)
                messages.append(error_message)
                return

        task_arr.append(step_name)

    order_mapping_initial = set_step_order({}, step_source)
    # Handle dependent that are defined before the dependencies step
    order_mapping_final = set_step_order(order_mapping_initial, step_source)

    logging.info(f"Order Mapping: {order_mapping_final}")
    logging.info(f"Task Sequence: {task_arr}")
    logging.info("Task Details:")
    logging.info(task_details)

    try:
        logging.info(f"Creating job for workflow: {filename}")
        job = Job.objects.create(name=filename, runnable=True)
    except IntegrityError:
        error_message = f"A job with name '{filename}' already exists."
        logging.error(error_message)
        messages.append(error_message)
        return None

    for task_name in task_arr:
        try:
            task = Task.objects.get(name=task_name)
            Step.objects.create(job=job, task=task, ordering=order_mapping_final[task_name])
        except ObjectDoesNotExist:
            error_message = f"Task {task_name} does not exist in the database"
            logging.error(error_message)
            messages.append(error_message)

    messages.append(f"Job '{filename}' created with tasks: {', '.join(task_arr)}")
    return order_mapping_final


def set_step_order(order_mapping, step_source):
    logging.info(f"Step Source: {step_source}")
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

    return order_mapping