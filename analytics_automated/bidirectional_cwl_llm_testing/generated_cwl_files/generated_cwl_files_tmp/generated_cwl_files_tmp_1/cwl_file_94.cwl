cwlVersion: v1.0
class: CommandLineTool

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:latest

inputs:
  - id: input_file
    type: File
    label: Input file

outputs:
  - id: output_file
    type: File
    label: Output file

baseCommand: echo
arguments: ["Hello, World!"]