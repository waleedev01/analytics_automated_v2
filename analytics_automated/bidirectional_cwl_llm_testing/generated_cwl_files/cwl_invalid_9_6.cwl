cwlVersion: v1.0
class: CommandLineTool
requirements:
  - UnsupportedRequirement
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename).txt
baseCommand: echo

UnsupportedRequirement:
  foo: bar