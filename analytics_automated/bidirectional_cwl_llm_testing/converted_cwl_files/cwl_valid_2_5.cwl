cwlVersion: v1.2
class: Workflow
inputs:
  input-file:
    type: File
outputs:
  output-file:
    type: File
    outputSource: step2/output
steps:
  step1:
    run: step1.cwl
    in:
      input: input-file
    out: []
  step2:
    run: step2.cwl
    in:
      input: step1/output
    out: []
