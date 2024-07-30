cwlVersion: v1.0
class: CommandLineTool
inputs:
  message:
    type: string
    inputBinding:
      position: 1
baseCommand: echo
arguments:
  - valueFrom: $(inputs.message)