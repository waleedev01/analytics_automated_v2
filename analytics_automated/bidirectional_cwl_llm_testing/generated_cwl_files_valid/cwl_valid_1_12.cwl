cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: Any
    inputBinding:
      position: 1
outputs:
  output_message:
    type: Any
    outputBinding:
      glob: "."