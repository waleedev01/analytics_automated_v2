cwlVersion: v1.0
class: Workflow

inputs:
  input_file:
    type: File
    label: Input File

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt

steps:
  step1:
    run: tool.cwl
    in:
      input: input_file
    out:
      output: output.txt