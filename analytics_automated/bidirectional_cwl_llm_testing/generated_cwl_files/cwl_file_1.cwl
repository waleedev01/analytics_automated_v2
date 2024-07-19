cwlVersion: v1.2
class: CommandLineTool

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: --input

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt