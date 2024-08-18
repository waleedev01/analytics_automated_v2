cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File
  input_string:
    type: string

outputs:
  final_output:
    type: File
    outputSource: step2/output_file

steps:
  step1:
    run: echo_tool.cwl
    in:
      message: input_string
    out:
      - output

  step2:
    run: cat_file_tool.cwl
    in:
      input_file: input_file
      input_string: step1/output
    out:
      - output_file

