cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

stdout: output.txt

baseCommand: cat

invalidField: missing required field