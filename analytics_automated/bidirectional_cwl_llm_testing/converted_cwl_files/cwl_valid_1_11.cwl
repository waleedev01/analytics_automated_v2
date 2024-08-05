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
outputs:
  output_0:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename).out
requirements: []
shellQuote: false
