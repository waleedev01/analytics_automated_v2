cwlVersion: v1.2
class: CommandLineTool
baseCommand: [sh, -c]
arguments:
  - |
    cat $(inputs.input_file.path) > output.txt
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
