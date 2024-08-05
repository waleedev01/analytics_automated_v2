cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - script.sh
  - --input
  - $I1
inputs:
  input_0:
    type: File
    inputBinding:
      position: 1
outputs:
  output_0:
    type: File
    outputBinding:
      glob: output.txt
requirements: []
shellQuote: false
