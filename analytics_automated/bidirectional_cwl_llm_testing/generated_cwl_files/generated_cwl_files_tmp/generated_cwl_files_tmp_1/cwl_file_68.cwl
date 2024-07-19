cwlVersion: v1.0

steps:
  - id: step1
    run: script.sh
    inputs:
      input_file:
        type: File
    outputs:
      output_file:
        type: File