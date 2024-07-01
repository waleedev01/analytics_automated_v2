import pytest
from analytics_automated.cwl_utils.cwl_workflow_handler import parse_cwl_workflow
from analytics_automated.models import Job, Task, Step
from django.test import TestCase
from analytics_automated.models import Backend, QueueType

class SetupBackendQueueTestCase(TestCase):
    def setUp(self):
        queue_type, created = QueueType.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'execution_behaviour': 1})
        Backend.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'queue_type': queue_type, 'root_path': '/tmp/'})

@pytest.mark.django_db
class TestCWLWorkflowHandler(SetupBackendQueueTestCase):
    def test_parse_cwl_workflow(self):
        cwl_data = {
            "class": "Workflow",
            "steps": {
                "step1": {
                    "run": {"class": "CommandLineTool", "baseCommand": "echo"},
                    "in": {},
                    "out": ["output1"]
                }
            }
        }
        messages = []
        order_mapping = parse_cwl_workflow(cwl_data, "test_workflow", messages)
        assert order_mapping is not None
        assert Job.objects.filter(name="test_workflow").exists()
        assert Task.objects.filter(name="step1").exists()
        assert Step.objects.filter(job__name="test_workflow", task__name="step1").exists()
