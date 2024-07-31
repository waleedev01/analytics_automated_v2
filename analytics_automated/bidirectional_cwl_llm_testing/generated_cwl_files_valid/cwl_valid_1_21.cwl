cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  - id: input_message
    type: Any
    inputBinding:
      position: 1
outputs:
  - id: output_message
    type: Any
    outputBinding:
      glob: $(inputs.input_message)