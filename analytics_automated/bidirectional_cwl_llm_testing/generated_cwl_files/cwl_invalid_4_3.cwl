cwlVersion: v1.2
inputs:
  input_file:
    type: File
outputs:
  output_file:
    type: File
baseCommand: echo
arguments:
  - "Hello, world!"