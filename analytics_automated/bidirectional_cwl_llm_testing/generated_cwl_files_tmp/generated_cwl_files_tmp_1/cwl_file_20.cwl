cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

requirements:
  - class: InlineJavascriptRequirement

arguments:
  - prefix: "---"

inputs:
  input_message:
    type: string

outputs:
  output_message:
    type: stdout