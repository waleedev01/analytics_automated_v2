cwlVersion: v1.0

class: CommandLineTool

baseCommand:
  - echo

inputs:
  input_message:
    type: string

outputs:
  output_message:
    type: string

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:latest

hints:
  - class: ShellCommandRequirement

label: Echo tool

doc: This tool echoes the input message to the output.

stdout: output.txt