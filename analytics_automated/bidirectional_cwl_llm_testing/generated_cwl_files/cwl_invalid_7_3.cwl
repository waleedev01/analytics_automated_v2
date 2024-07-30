cwlVersion: v1.3
class: CommandLineTool
inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1
outputs:
  - id: output_file
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename)
baseCommand: cat