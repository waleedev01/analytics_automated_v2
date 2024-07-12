cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  input_message:
    type: string
    label: "Message to echo"

outputs:
  output_message:
    type: stdout

hints:
  DockerRequirement:
    dockerPull: alpine:latest