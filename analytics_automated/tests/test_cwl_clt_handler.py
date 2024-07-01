import pytest
from django.test import TestCase
from analytics_automated.models import Backend, QueueType, Task
from analytics_automated.cwl_utils.cwl_clt_handler import save_task_to_db

class SetupBackendQueueTestCase(TestCase):
    def setUp(self):
        queue_type, created = QueueType.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'execution_behaviour': 1})
        Backend.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'queue_type': queue_type, 'root_path': '/tmp/'})

@pytest.mark.django_db
class TestCWLHandler(SetupBackendQueueTestCase):
    def test_save_task_to_db(self):
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
