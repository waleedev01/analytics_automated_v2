import yaml
import logging
import pytest
from django.test import TestCase
from analytics_automated.models import Backend, QueueType
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

logger = logging.getLogger(__name__)

class SetupBackendQueueTestCase(TestCase):
    def setUp(self):
        queue_type, created = QueueType.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'execution_behaviour': 1})
        Backend.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'queue_type': queue_type, 'root_path': '/tmp/'})

@pytest.mark.django_db
class TestCWLParser(SetupBackendQueueTestCase):

    @pytest.mark.usefixtures("tmpdir")
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
