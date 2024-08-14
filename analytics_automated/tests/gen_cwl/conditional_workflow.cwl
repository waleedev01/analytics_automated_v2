cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File
    outputSource: step2/output_file

steps:
  step1:
    run: cat_file_tool.cwl
    in:
      input_file: input_file
    out:
      - output_file

  step2:
    run: concat_tool.cwl
    in:
      file1: step1/output_file
      file2: step1/output_file
    out:
      - output_file
