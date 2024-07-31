cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  input_message:
    type: any
    inputBinding:
      position: 1
outputs:
  output_message:
    type: any