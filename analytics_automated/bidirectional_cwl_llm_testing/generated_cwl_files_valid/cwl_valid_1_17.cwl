cwlVersion: v1.2
class: CommandLineTool
baseCommand: ["echo", "Hello, world!"]
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