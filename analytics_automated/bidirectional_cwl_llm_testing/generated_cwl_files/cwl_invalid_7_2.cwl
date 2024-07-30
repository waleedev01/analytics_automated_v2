cwlVersion: v2.0
class: CommandLineTool
inputs:
  input_file:
    type: File
outputs:
  output_file:
    type: File
baseCommand: cat input_file > output_file