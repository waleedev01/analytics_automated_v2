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

stdout: output.txt

baseCommand: echo

arguments:
  - valueFrom: $(inputs.input_file.path)