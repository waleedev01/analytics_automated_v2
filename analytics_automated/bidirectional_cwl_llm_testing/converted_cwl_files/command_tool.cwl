cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - echo
  - $P1
inputs:
  command_tool_input_message:
    type: File
    inputBinding:
      position: 1
outputs: {}
