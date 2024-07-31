cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

steps:
  step1:
    run: step1.cwl
    in:
      input_file: input_file
    out:
      output_file: output_file

outputs:
  output_file:
    type: File
    outputSource: step1/output_file