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

baseCommand: echo

label: Invalid CWL File 

stdout: output.txt