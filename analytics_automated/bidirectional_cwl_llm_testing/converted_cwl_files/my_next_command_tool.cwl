cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - next_command_tool
  - $I1
inputs: {}
outputs:
  output_my_next_command_tool:
    type: File
    outputBinding:
      glob: '*.out'
