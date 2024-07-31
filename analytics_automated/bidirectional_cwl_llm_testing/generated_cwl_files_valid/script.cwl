cwlVersion: v1.0
class: CommandLineTool
baseCommand: script.sh

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