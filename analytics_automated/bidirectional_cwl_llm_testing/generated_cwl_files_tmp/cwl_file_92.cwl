cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

stdout: output.txt

baseCommand: echo

arguments:
  - valueFrom: "Hello, world!"