cwlVersion: v1.0

class: CommandLineTool

baseCommand:
  - echo

inputs:
  - id: message
    type: string

outputs:
  - id: output_message
    type: string

requirements:
  DockerRequirement:
    dockerPull: alpine:latest

stdout:
  output_message

stderr: error.log