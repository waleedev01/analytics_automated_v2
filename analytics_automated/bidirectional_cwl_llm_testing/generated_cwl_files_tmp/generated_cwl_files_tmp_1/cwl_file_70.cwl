cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  input_file:
    type: File
  output_file:
    type: File

outputs:
  output_file:
    type: File

requirements:
  InlineJavascriptRequirement: {}

hints:
  DockerRequirement:
    dockerPull: ubuntu:latest

label: Missing Required Fields CWL File