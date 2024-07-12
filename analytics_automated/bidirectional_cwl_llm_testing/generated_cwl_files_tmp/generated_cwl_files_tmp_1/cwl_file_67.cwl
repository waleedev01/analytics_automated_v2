cwlVersion: v1.1
class: CommandLineTool
baseCommand: echo
requirements:
  - class: InlineJavascriptRequirement
inputs:
  message:
    type: string
    inputBinding:
      position: 1
      prefix: "--message"
outputs: []