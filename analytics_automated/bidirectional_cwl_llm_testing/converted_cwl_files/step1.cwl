cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
  - $P2
inputs:
  step1_input1:
    type: File
    inputBinding:
      position: 1
  step1_input2:
    type: File
    inputBinding:
      position: 1
outputs: {}
