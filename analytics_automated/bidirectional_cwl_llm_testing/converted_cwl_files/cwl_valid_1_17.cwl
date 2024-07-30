cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $I1
  - Hello,
  - world!
inputs: {}
outputs:
  output_cwl_valid_1_17:
    type: File
    outputBinding:
      glob: '*.txt'
