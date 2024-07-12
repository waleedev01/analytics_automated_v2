cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input_message:
    type: string
    inputBinding:
      position: 1
outputs: []
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.input_message)
        entryname: message.txt
stdout: message.txt