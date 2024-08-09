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
stdin: 123  # Invalid, should be a string
stdout: output.txt
stderr: error.txt
