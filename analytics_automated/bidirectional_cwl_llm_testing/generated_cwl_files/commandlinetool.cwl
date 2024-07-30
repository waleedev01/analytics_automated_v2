cwlVersion: v1.1
class: CommandLineTool
baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1
      prefix: "-n"

outputs:
  output_message:
    type: stdout