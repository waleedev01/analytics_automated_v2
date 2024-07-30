cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  tool_input_string:
    type: File
    inputBinding:
      position: 1
outputs: {}
