cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

baseCommand: echo

stdout: output.txt