cwlVersion: v1.0
class: CommandLineTool

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

requirements:
  - class: DockerRequirement

baseCommand: echo

stdout: output.txt