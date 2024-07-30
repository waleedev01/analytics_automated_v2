cwlVersion: v1.0
class: CommandLineTool
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
baseCommand: cat
args:
  - $(inputs.input_file.path)