cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_file:
    type: File

steps:
  step1:
    run: step1.cwl
    in:
      input_file: input_file
    out:
      - output_file

  step2:
    run: step2.cwl
    in:
      input_file: step1/output_file
    out:
      - output_file