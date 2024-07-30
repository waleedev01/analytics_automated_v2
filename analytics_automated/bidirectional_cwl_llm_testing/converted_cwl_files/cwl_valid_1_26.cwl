cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  cwl_valid_1_26_input_message:
    type: File
    inputBinding:
      position: 1
outputs: {}
