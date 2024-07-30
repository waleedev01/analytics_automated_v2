cwlVersion: v1.0
inputs:
  - id: input_file
    type: File
outputs:
  - id: output_file
    type: File
baseCommand: echo 'Hello, World!'