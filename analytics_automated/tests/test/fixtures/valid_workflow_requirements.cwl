cwlVersion: v1.0
class: Workflow
inputs:
  input1:
    type: File
outputs:
  output1:
    type: File
    outputSource: step1/output
steps:
  step1:
    run: some_tool.cwl
    in:
      input1: input1
    out: [output]
requirements:
  - class: EnvVarRequirement
