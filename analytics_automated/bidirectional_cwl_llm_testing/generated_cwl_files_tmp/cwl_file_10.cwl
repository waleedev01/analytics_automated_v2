cwlVersion: v1.0
cwl_tool:
  inputs:
    input_file:
      type: File
    output_file:
      type: File
  outputs:
    output_file:
      type: File
  steps:
    step1:
      run: script.sh
      in:
        input_file: input_file
      out:
        output_file: output_file