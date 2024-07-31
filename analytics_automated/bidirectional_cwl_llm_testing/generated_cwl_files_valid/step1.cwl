cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  input1:
    type: string
    inputBinding:
      position: 1
      prefix: "-i"
  input2:
    type: string
    inputBinding:
      position: 2
      prefix: "-o"

outputs:
  output1:
    type: stdout