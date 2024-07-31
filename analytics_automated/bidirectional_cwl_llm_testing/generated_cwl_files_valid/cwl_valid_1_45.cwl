cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo

inputs:
  input_message:
    type: string
    inputBinding:
      position: 1
      prefix: "--message"

outputs:
  output_message:
    type: string
    outputBinding:
      glob: $(inputs.input_message)