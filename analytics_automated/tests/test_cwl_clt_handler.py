import pytest
from analytics_automated.cwl_utils.cwl_clt_handler import parse_cwl_clt, save_task_to_db
from analytics_automated.models import Task, Parameter

@pytest.mark.django_db
def test_parse_cwl_clt():
    cwl_data = {
        "baseCommand": "echo",
        "inputs": {"input1": {"type": "string"}},
        "outputs": {"output1": {"type": "stdout"}},
    }
    name = "echo_task"
    task = parse_cwl_clt(cwl_data, name)
    assert task['name'] == name
    assert task['base_command'] == "echo"
    assert 'inputs' in task
    assert 'outputs' in task

@pytest.mark.django_db
def test_save_task_to_db():
    task_data = {
        "name": "echo_task",
        "base_command": "echo",
        "inputs": [],
        "outputs": [],
        "requirements": [],
        "hints": [],
        "arguments": [],
        "stdin": None,
        "stdout": None,
        "stderr": None,
        "success_codes": [],
        "temporary_fail_codes": [],
        "permanent_fail_codes": [],
        "label": None,
        "doc": None,
        "initial_work_dir": None,
        "shell_quote": False,
        "executable": "echo",
        "in_glob": "",
        "out_glob": "",
        "stdout_glob": "",
    }
    messages = []
    task = save_task_to_db(task_data, messages)
    assert task is not None
    assert Task.objects.filter(name="echo_task").exists()
    assert "Task saved successfully" in messages[0]
