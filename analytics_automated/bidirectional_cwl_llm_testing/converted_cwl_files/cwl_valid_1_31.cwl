cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  cwl_valid_1_31_first_input:
    type: File
    inputBinding:
      position: 1
outputs: {}
