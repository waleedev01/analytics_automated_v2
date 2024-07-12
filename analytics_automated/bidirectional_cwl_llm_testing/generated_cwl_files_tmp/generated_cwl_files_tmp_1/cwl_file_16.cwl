cwlVersion: v1.0
class: CommandLineTool

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

steps:
  run: echo
  in:
    stdin: $(inputs.input_file)