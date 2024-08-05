cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - step3.sh
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
      glob: .out
requirements: []
shellQuote: false
