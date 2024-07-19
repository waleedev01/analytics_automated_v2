cwlVersion: v1.0

class: CommandLineTool

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

stdout: output.txt

baseCommand: cat

requirements:
  class: InlineJavascriptRequirement

invalid_field: value

description: This is a sample CWL file with missing required fields.