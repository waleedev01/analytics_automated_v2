cwlVersion: v1.0

class: CommandLineTool

baseCommand:
  - echo

inputs:
  message:
    type: string

outputs:
  stdout:
    type: stdout

requirements:
  InlineJavascriptRequirement:

hints:
  DockerRequirement:
    dockerPull: alpine:3.9