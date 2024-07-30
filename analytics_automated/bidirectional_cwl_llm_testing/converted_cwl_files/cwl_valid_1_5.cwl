cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  cwl_valid_1_5_input_file:
    type: File
    inputBinding:
      position: 1
outputs: {}
