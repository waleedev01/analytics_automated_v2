cwlVersion: v1.2

class: CommandLineTool

baseCommand: echo

inputs:
  input_message:
    type: string

outputs:
  output_message:
    type: string