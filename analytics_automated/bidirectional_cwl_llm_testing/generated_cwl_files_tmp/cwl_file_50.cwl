cwlVersion: v1.0

class: CommandLineTool

inputs:
  input_file:
    type: File
    label: "Input file"

outputs:
  output_file:
    type: File
    label: "Output file"

requirements:
  - class: InlineJavascriptRequirement

stdout: output.txt