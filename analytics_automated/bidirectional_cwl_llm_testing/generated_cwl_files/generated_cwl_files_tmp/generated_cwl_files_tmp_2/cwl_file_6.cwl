cwlVersion: v1.0
class: CommandLineTool

inputs:
  invalid_input:
    type: string

outputs:
  invalid_output:
    type: string

arguments:
  - valueFrom: echo "Invalid CWL file with missing required fields"

baseCommand: echo

invalid_field: missing_required_field