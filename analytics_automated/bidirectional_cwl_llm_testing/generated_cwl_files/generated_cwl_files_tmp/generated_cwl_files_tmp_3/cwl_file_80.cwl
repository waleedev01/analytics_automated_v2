cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  - id: input_msg
    type: string

outputs:
  - id: output_msg
    type: stdout