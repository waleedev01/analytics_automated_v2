cwlVersion: v1.2
class: Workflow

inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1
      prefix: --input

steps:
  step1:
    run: step1.cwl
    in:
      input_file: input_file
    out:
      - id: output_file
        type: File

outputs:
  - id: final_output
    type: File
    outputSource: step1/output_file