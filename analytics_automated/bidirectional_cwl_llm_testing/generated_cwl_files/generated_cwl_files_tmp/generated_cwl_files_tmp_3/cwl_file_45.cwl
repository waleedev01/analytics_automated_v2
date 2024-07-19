cwlVersion: v1.0
class: CommandLineTool
id: my-tool.cwl
baseCommand: echo

inputs:
  input_message:
    type: string
    inputBinding:
      position: 1
      prefix: "Message:"

outputs:
  output_message:
    type: stdout

requirements:
  - class: ShellCommandRequirement