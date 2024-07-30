cwlVersion: v1.3
class: CommandLineTool
inputs:
  input_file:
    type: File
outputs:
  output_file:
    type: File
baseCommand: echo