cwlVersion: v1.0
class: CommandLineTool
requirements:
  - class: InlineJavascriptRequirement
  - class: UnsupportedRequirement
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename)
baseCommand: echo
  - "$(inputs.input_file.path)" > "$(outputs.output_file.path)"