cwlVersion: v1.2
class: Workflow

inputs:
  input_file1: File
  input_file2: File
  param1: string?

outputs:
  output_file: File

steps:
  step1:
    run: ./step1.cwl
    in:
      input_file: input_file1
      param: param1
    out:
      output_file

  step2:
    run: ./step2.cwl
    in:
      input_file: step1/output_file
    out:
      output_file

requirements:
  InlineJavascriptRequirement: {}
  SubworkflowFeatureRequirement: {}