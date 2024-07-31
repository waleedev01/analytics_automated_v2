cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1
outputs:
  - id: output_file
    type: File
    outputBinding:
      glob: $(inputs.input_file.path)