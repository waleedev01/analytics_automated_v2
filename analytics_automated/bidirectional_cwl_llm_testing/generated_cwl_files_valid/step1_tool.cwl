cwlVersion: v1.0
class: CommandLineTool
baseCommand: step1_tool.py

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: --input

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output_file.txt