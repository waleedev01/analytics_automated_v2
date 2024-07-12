cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
outputs: []
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entryname: message.txt
        entry: $(inputs.message)
      - entryname: output.txt
        entry: $(inputs.message)
  ShellCommandRequirement: {}