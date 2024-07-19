cwlVersion: v1.0

class: CommandLineTool

label: Example Tool

description: This is an example tool that demonstrates missing required fields in a CWL file.

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

requirements:
  - class: DockerRequirement

hints:
  DockerRequirement:
    dockerPull: ubuntu:latest