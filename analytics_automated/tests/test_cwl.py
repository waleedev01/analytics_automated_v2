import yaml
import logging
import pytest
from django.test import TestCase
from analytics_automated.models import Backend, QueueType
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def setup_backend_queue(db):
    queue_type, created = QueueType.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'execution_behaviour': 1})
    Backend.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'queue_type': queue_type, 'root_path': '/tmp/'})

@pytest.mark.django_db
class TestCWLParser:

    @pytest.mark.usefixtures("setup_backend_queue")
    def test_read_cwl_file(self, tmpdir):
        cwl_content = """
        cwlVersion: v1.2
        class: CommandLineTool
        baseCommand: echo
        inputs:
          input1:
            type: File
        outputs:
          output1:
            type: File
        """
        cwl_file = tmpdir.join("echo.cwl")
        cwl_file.write(cwl_content)

        messages = []
        task = read_cwl_file(str(cwl_file), "echo.cwl", messages)
        assert task is not None

