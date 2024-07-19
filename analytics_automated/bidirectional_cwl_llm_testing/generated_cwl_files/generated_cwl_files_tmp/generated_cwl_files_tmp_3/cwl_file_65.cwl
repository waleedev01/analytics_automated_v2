cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
      prefix: "Message: "
outputs:
  output_message:
    type: stdout