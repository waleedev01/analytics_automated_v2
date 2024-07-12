cwlVersion: v1.0
class: CommandLineTool

inputs:
  - id: input_file
    type: File
    label: Input file

outputs:
  - id: output_file
    type: File
    label: Output file

requirements:
  DockerRequirement:
    dockerPull: alpine:latest

stdout: output.txt