cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo

inputs:
  input1:
    type: string
    inputBinding:
      position: 1

outputs:
  output1:
    type: stdout