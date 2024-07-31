cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  input1:
    type: any
    inputBinding:
      position: 1
outputs:
  output1:
    type: any