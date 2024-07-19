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
    dockerPull: alpine:latest

command: echo "Hello, World!" > output_file