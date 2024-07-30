cwlVersion: v1.0
class: CommandLineTool
requirements:
  - unsupportedRequirement
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: echo 'Hello, world!'