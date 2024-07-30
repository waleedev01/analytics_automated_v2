cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  CommandLineTool4_input1:
    type: File
    inputBinding:
      position: 1
outputs: {}
