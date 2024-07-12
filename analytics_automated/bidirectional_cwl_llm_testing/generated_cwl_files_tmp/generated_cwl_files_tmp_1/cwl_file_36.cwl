cwlVersion: v1.0

class: CommandLineTool

baseCommand: echo

inputs:
  input_message:
    type: string
    label: "Input Message"

outputs:
  output_message:
    type: stdout

requirements:
  - class: DockerRequirement
    dockerPull: alpine:latest

stdout: output_message