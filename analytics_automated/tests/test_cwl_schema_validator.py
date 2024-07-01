import pytest
from analytics_automated.cwl_utils.cwl_schema_validator import CWLSchemaValidator

def test_validate_cwl():
    cwl_data = {
        "cwlVersion": "v1.2",
        "class": "CommandLineTool",
        "baseCommand": "echo"
    }
    validator = CWLSchemaValidator()
    is_valid, message = validator.validate_cwl(cwl_data)
    assert is_valid
    assert message == "CWL file is valid."

def test_validate_cwl_missing_class():
    cwl_data = {
        "cwlVersion": "v1.2"
    }
    validator = CWLSchemaValidator()
    is_valid, message = validator.validate_cwl(cwl_data)
    assert not is_valid
    assert "Missing 'class' in CWL file" in message
