cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  - id: message
    type: string

outputs:
  - id: output
    type: stdout