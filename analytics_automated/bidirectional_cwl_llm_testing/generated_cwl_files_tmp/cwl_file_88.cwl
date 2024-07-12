cwlVersion: v1.0
class: CommandLineTool
inputs:
  input_file:
    type: File
    label: Input File
outputs:
  output_file:
    type: File
    label: Output File
baseCommand: echo
requirements:
  class: InlineJavascriptRequirement
stdout: output.txt