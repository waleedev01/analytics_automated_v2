cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File
outputs:
  output_file_0:
    type: File
    outputSource: step1/output_0
steps:
  step1:
    run: step1.cwl
    in:
      input_0: input_file
    out: []
requirements: []
