cwlVersion: v1.2

class: CommandLineTool

inputs:
  input_file:
    type: File
    label: "Input file"

outputs:
  output_file:
    type: File
    label: "Output file"

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:latest

ids: missing_fields

label: "Missing Fields Workflow"