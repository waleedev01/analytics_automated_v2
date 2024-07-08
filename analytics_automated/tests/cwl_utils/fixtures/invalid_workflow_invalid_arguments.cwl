cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input1:
    type: string
outputs:
  output1:
    type: stdout
arguments: -n  # Invalid, should be a list
stdin: input.txt
stdout: output.txt
stderr: error.txt
