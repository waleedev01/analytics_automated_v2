cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  cwl_valid_1_46_input1:
    type: File
    inputBinding:
      position: 1
outputs: {}
