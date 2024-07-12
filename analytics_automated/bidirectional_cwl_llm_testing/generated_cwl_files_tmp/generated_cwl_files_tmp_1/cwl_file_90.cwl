cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  - id: input_message

outputs:
  - id: output_message

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:latest