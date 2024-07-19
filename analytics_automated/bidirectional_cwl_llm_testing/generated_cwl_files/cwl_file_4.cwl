cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

outputs:
  output_file:
    type: stdout

requirements:
  InlineJavascriptRequirement: {}

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File
    outputBinding:
      glob: "output.txt"