cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input1:
    type: string
outputs:
  output1:
    type: stdout
arguments:
  - "-n"
stdin: input.txt
stdout: output.txt
stderr: 789  # Invalid, should be a string
