cwlVersion: v1.0

class: CommandLineTool

baseCommand:
  - echo

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

requirements:
  DockerRequirement:
    dockerPull: alpine:latest