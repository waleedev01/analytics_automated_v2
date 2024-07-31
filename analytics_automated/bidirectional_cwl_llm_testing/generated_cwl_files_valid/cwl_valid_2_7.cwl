cwlVersion: v1.2
class: Workflow

inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1

outputs:
  - id: output_file
    type: File
    outputSource: step1/output_file

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