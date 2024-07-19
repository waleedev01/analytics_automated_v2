cwlVersion: v1.0
class: CommandLineTool
inputs:
  - id: input_file
    type: String
outputs:
  - id: output_file
    type: File
baseCommand: echo "Hello, world!"