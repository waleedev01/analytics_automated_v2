cwlVersion: v1.0

# This CWL file is invalid due to the missing required fields

class: CommandLineTool

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:latest

stdout: output_file
stderr: error.txt