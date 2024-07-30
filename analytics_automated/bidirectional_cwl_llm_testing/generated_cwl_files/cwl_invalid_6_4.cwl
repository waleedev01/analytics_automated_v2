cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  msg:
    type: string
    inputBinding:
      shellQuote: false