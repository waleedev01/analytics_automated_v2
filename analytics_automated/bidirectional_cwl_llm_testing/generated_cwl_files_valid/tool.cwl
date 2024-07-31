cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo

inputs:
  input_string:
    type: string
    inputBinding:
      position: 1
      prefix: "Input:"

outputs:
  output_string:
    type: stdout