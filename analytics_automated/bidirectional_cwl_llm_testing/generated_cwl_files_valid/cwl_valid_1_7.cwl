cwlVersion: v1.2
class: CommandLineTool
baseCommand:
  - echo
inputs:
  input_file:
    type: Any
    inputBinding:
      position: 1
outputs:
  output_file:
    type: Any
    outputBinding:
      glob: output.txt