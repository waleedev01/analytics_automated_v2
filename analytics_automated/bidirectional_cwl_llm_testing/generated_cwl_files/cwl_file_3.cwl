cwlVersion: v1.0
inputs:
  input_file:
    type: File
outputs:
  output_file:
    type: File
baseCommand: cat data.txt
requirements:
  - class: ShellCommandRequirement