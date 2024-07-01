import pytest
import os
from analytics_automated.cwl_utils.cwl_parser import read_cwl_file

@pytest.mark.django_db
def test_read_cwl_file(tmpdir):
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
    assert "echo" in task.name
    assert len(messages) == 0
