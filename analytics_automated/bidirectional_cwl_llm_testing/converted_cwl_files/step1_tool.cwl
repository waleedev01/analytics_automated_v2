cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - step1_tool.py
  - --input
  - $I1
inputs:
  input_0:
    type: File
    inputBinding:
      position: 1
outputs:
  output_0:
    type: File
    outputBinding:
      glob: output_file.txt
requirements: []
shellQuote: false
