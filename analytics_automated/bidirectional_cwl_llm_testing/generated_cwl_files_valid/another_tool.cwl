cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo

inputs:
  input_message:
    type: string
    inputBinding:
      position: 1
      prefix: "Message: "

outputs:
  echoed_message:
    type: stdout