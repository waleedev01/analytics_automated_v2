cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  my_input:
    type: string

outputs:
  my_output:
    type: stdout