cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

steps:
  step1:
    run: step1.cwl
    in:
      input: input_file
    out:
      output: output_file

  step2:
    run: step2.cwl
    in:
      input: step1/output_file
    out:
      output: final_output

baseCommand:
  - echo
  - "Hello, World!"