cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo

inputs:
  input_message:
    type: string
    inputBinding:
      position: 1
      prefix: "Message: "

outputs:
  output_message:
    type: stdout