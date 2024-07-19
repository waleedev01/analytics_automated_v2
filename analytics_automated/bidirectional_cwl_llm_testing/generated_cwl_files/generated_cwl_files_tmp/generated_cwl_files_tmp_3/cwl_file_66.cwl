cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  - id: message
    type: string

outputs:
  - id: output_message
    type: stdout

requirements:
  - class: InlineJavascriptRequirement

invalidField: missing_required_field