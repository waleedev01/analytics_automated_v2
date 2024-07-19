cwlVersion: v1.0

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

steps:
  - id: step1
    run: tool.cwl
    in:
      input_file: input_file
    out:
      output_file: output_file