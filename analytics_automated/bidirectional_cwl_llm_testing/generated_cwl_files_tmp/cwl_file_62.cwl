cwlVersion: v1.0

class: CommandLineTool

inputs:
  - id: input_file
  type: File

outputs:
  - id: output_file
  type: File

cmd: cat $(inputs.input_file.path) > $(outputs.output_file.path)