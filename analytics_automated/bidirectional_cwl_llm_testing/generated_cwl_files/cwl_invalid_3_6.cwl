class:
  CommandLineTool
inputs:
  - id: input_file
    type: File
    label: "Input File"
outputs:
  - id: output_file
    type: File
    label: "Output File"
baseCommand: cat