cwlVersion: v1.3
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
      glob: "output.txt"
baseCommand: echo "Hello, World!"