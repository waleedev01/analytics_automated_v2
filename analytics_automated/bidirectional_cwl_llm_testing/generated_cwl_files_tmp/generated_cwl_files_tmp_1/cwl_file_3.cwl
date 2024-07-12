cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
requirements:
  - class: InlineJavascriptRequirement
inputs:
  message:
    type: string
    inputBinding:
      position: 1
      prefix: "Input message: "
outputs:
  output_message:
    type: stdout
stdout: output.txt