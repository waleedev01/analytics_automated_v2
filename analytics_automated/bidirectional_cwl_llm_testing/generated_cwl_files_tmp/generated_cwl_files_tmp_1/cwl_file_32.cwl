cwlVersion: v1.0

# Missing required fields
inputs:
  data:
    type: File

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt

steps:
  step1:
    run: echo.txt
    in:
      input_file: data
    out:
      output_file: output.txt