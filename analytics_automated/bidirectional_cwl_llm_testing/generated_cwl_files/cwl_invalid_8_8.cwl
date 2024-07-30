cwlVersion: v1.0
class: InvalidTool
inputs:
  input1:
    type: string
    inputBinding:
      position: 1
outputs:
  output1:
    type: string
    outputBinding:
      glob: $(inputs.input1)
baseCommand: echo