cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $I1
inputs: {}
outputs:
  output_cwl_valid_1_11:
    type: File
    outputBinding:
      glob: '*.out'
