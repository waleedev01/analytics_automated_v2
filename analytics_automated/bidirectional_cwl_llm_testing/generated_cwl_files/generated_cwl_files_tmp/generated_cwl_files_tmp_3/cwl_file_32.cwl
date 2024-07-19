cwlVersion: v1.0

class: Workflow

inputs:
  parameter1:
    type: string

steps:
  step1:
    run: tool.cwl
    in:
      input1: parameter1

outputs:
  output1:
    type: File
    outputSource: step1/output1