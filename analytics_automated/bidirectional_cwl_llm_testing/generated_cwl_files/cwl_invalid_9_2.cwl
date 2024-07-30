cwlVersion: v1.0
class: CommandLineTool
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
baseCommand: cat
requirements:
  - CustomRequirement: true