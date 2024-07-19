cwlVersion: v1.0
class: CommandLineTool

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

requirements:
  - class: DockerRequirement

# Missing required fields: baseCommand, stdout, stderr