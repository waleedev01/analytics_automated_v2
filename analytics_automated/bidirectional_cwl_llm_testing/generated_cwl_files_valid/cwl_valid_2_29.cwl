cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File

outputs:
  output_file:
   type: File
   outputSource: step1/output

steps:
  step1:
    run: step1.cwl
    in:
      input_file: input_file
    out:
      - output

  step2:
    run: step2.cwl
    in:
      input_file: step1/output
    out:
      - output