cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  tool2_message:
    type: File
    inputBinding:
      position: 1
outputs: {}
