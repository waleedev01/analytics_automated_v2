import yaml
import logging
import pytest
from analytics_automated.models import Backend, QueueType
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def setup_backend_queue(db):
    queue_type, created = QueueType.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'execution_behaviour': 1})
    Backend.objects.get_or_create(pk=1, defaults={'name': 'localhost', 'queue_type': queue_type, 'root_path': '/tmp/'})

@pytest.mark.django_db
@pytest.mark.usefixtures("setup_backend_queue")
class TestCWLParser:

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

    def test_read_cwl_file_invalid(self, tmpdir):
        cwl_content = """
        cwlVersion: v1.2
        class: InvalidClass
        baseCommand: echo
        inputs:
          input1:
            type: string
        outputs:
          output1:
            type: stdout
        """
        cwl_file = tmpdir.join("invalid.cwl")
        cwl_file.write(cwl_content)

        messages = []
        task = read_cwl_file(str(cwl_file), "invalid.cwl", messages)
        assert task is None
        assert "Unknown CWL class for file" in messages[0]