cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs: {}
outputs:
  output_0:
    type: File
    outputBinding:
      glob: output.txt
requirements: []
shellQuote: false
