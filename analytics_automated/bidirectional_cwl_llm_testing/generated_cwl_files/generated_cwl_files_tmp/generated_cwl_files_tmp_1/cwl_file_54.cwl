cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  input_message: string

outputs:
  output_message:
    type: stdout