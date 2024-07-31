cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  input_message:
    type: string
    inputBinding:
      prefix: -m
outputs:
  output_message:
    type: stdout