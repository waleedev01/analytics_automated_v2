cwlVersion: v1.2
class: CommandLineTool
baseCommand: ls
inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1
outputs:
  - id: output_file
    type: File