cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1
      prefix: "Message: "
    doc: "The message to be echoed."

outputs:
  output_message:
    type: stdout

requirements:
  InlineJavascriptRequirement: {}

stdout: output.txt