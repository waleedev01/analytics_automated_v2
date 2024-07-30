cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - myscript.py
  - $I1
inputs: {}
outputs:
  output_cwl_valid_1_38:
    type: File
    outputBinding:
      glob: '*.txt'
