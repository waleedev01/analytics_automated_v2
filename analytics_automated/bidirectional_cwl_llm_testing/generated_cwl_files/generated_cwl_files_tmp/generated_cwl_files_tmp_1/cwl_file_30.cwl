cwlVersion: v1.0

inputs:
  input_file:
    type: File
    format: edam:format_2330

outputs:
  output_file:
    type: File
    format: edam:format_2330

steps:
  step1:
    run: echo.cwl
    in:
      input_file: input_file
    out:
      - output_file