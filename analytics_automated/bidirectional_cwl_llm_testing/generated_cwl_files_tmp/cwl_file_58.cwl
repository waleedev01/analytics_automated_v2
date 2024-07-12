cwlVersion: v1.0

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

steps:
  step1:
    run: script.sh
    in:
      input: input_file
    out:
      output: output_file