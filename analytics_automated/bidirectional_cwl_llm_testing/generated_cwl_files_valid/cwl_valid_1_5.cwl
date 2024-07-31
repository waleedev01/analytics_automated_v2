cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input_file:
    type: string
    inputBinding:
      position: 1
outputs:
  output_file:
    type: string
    outputBinding:
      glob: $(inputs.input_file)