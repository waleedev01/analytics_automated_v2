cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input_string:
    type: string
    inputBinding:
      position: 1
outputs:
  output_string:
    type: string
    outputBinding:
      glob: $(inputs.input_string)
      loadContents: true