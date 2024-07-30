cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
  - Hello,
  - World!
inputs:
  cwl_valid_1_25_input1:
    type: File
    inputBinding:
      position: 1
outputs: {}
