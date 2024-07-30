cwlVersion: v1.2
class: Workflow
inputs:
  input-file:
    type: File
outputs:
  output-file:
    type: File
    outputSource: step1/output
steps:
  step1:
    run: step1.cwl
    in:
      input: input-file
    out: []
