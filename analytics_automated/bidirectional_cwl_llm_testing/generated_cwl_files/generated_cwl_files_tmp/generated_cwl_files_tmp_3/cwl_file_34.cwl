cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  inputMessage:
    type: string
    label: The input message

outputs:
  outputMessage:
    type: string
    outputBinding:
      glob: output.txt