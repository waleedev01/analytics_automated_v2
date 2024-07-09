cwlVersion: v1.0
class: Workflow
inputs:
  input1:
    type: File
outputs:
  output1:
    type: File
    outputSource: step1/output
