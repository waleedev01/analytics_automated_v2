cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $I1
  - Hello,
  - world!
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
