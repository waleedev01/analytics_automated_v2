cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  input_message:
    type: string

outputs:
  output_message:
    type: stdout