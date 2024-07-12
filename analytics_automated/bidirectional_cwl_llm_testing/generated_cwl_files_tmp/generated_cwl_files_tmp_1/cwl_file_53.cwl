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
stdin: input_message
stdout: $(inputs.input_message)
stderr: $(inputs.input_message)