cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  - id: input_message
    type: string
    inputBinding:
      position: 1
outputs:
  - id: output_message
    type: string
    outputBinding:
      glob: $(inputs.input_message)