cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

requirements:
  - class: InlineJavascriptRequirement

stdout: output.txt

stderr: error.txt