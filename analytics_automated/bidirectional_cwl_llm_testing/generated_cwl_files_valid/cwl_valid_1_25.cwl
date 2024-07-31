cwlVersion: v1.2
class: CommandLineTool
baseCommand: [echo, "Hello, World!"]
inputs:
  input1:
    type: string
    inputBinding:
      position: 1
outputs:
  output1:
    type: stdout