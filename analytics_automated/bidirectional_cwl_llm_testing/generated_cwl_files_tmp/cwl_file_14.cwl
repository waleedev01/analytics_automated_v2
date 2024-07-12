cwlVersion: v1.0
class: CommandLineTool
inputs:
  input_file:
    type: File
outputs:
  output_file:
    type: File
requirements:
  DockerRequirement:
    dockerPull: ubuntu:latest
arguments:
  - valueFrom: $(inputs.input_file)
    prefix: --input_file
baseCommand: cat
stdout: output.txt