cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $I1
inputs:
  input_0:
    type: File
    inputBinding:
      position: 1
outputs: {}
requirements: []
shellQuote: false
