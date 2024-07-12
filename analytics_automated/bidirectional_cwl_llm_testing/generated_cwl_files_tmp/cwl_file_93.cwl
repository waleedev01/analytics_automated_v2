cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
arguments:
  message:
    type: string
    inputBinding:
      position: 1
inputs:
  message:
    type: string
    inputBinding:
      position: 2
outputs: []