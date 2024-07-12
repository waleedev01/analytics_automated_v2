cwlVersion: v1.0
class: CommandLineTool

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

requirements:
  - class: InlineJavascriptRequirement

stdout: output.txt

baseCommand: echo

InvalidField: This is an invalid field in a CWL file.