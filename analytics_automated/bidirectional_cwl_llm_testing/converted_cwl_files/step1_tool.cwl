cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - step1_tool.py
  - --input
  - $I1
inputs: {}
outputs:
  output_step1_tool:
    type: File
    outputBinding:
      glob: '*.txt'
