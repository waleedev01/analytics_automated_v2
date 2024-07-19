cwlVersion: v1.0
class: CommandLineTool

requirements:
  - class: DockerRequirement
    dockerPull: alpine:3.10

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

stdout: output.txt

baseCommand: echo

error: This CWL file is missing required fields.