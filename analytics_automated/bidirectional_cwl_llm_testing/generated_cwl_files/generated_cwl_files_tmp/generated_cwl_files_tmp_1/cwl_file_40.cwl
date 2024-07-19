cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  - id: input1
    type: string

outputs:
  - id: output1
    type: string