cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  2ndCommandLineTool_message:
    type: File
    inputBinding:
      position: 1
outputs: {}
