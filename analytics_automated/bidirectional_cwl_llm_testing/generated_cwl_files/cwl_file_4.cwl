cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
outputs:
  - id: output_message
    type: stdout

requirements:
  - class: InlineJavascriptRequirement

label: Echo tool
doc: |
  Simple tool to echo a message
hints: []

arguments: []

stdout: output_message