cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  - id: input_message
    type: string

outputs:
  - id: output_message
    type: stdout