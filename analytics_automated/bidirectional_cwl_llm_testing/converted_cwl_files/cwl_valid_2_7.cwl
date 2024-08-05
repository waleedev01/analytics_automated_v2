cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File
outputs:
  output_file_0:
    type: File
    outputSource: step3/output_0
steps:
  step1:
    run: step1.cwl
    in:
      input_0: input_file
    out: []
  step2:
    run: step2.cwl
    in:
      input_0: step1/output_0
    out: []
  step3:
    run: step3.cwl
    in:
      input_0: step2/output_0
    out:
      - output_0
requirements: []
