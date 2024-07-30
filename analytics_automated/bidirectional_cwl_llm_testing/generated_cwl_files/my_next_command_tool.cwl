cwlVersion: v1.0
class: CommandLineTool
baseCommand: next_command_tool
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename).out