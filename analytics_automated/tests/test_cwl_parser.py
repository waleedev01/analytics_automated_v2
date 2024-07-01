import pytest
import yaml
import logging
from analytics_automated.cwl_utils.cwl_schema_validator import CWLSchemaValidator
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file
from analytics_automated.models import Backend, QueueType
from django.test import TestCase

logger = logging.getLogger(__name__)

class SetupBackendQueueTestCase(TestCase):
    def setUp(self):
        queue_type, created = QueueType.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'execution_behaviour': 1})
        Backend.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'queue_type': queue_type, 'root_path': '/tmp/'})

@pytest.mark.django_db
class TestCWLParser(SetupBackendQueueTestCase):
    def test_read_cwl_file(self, tmpdir):
        cwl_content = """
        cwlVersion: v1.2
        class: CommandLineTool
        baseCommand: echo
        inputs:
          input1:
            type: string
        outputs:
          output1:
            type: stdout
        """
        cwl_file = tmpdir.join("echo.cwl")
        cwl_file.write(cwl_content)

        messages = []
        task = read_cwl_file(str(cwl_file), "echo.cwl", messages)
        assert task is not None

    def test_validate_cwl(self):
        cwl_content = {
            "cwlVersion": "v1.2",
            "class": "CommandLineTool",
            "baseCommand": "echo",
            "inputs": {
                "input1": {
                    "type": "string"
                }
            },
            "outputs": {
                "output1": {
                    "type": "stdout"
                }
            }
        }
        validator = CWLSchemaValidator()
        is_valid, message = validator.validate_cwl(cwl_content)
        assert is_valid

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
