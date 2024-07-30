cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_files:
    type: File[]

steps:
  step1:
    run: step1.cwl
    in:
      input_file: input_file
    out: 
      - output_file1

  step2:
    run: step2.cwl
    in:
      input_file: step1/output_file1
    out: 
      - output_file2

  step3:
    run: step3.cwl
    in:
      input_file: step2/output_file2
    out: 
      - output_files