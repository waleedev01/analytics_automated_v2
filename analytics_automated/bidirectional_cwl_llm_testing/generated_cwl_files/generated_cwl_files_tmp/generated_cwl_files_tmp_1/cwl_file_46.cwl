cwlVersion: v1.1

class: CommandLineTool

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

requirements:
  - class: DockerRequirement

stdout: output.txt

baseCommand: cat

arguments: []

exitCode: []

successCodes: []

invalid_field: missing_required_field

label: Invalid CWL file with missing required fields