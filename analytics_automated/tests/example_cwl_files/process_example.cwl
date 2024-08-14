cwlVersion: v1.2
class: CommandLineTool

baseCommand: echo
arguments:
  - valueFrom: "$(inputs.message)"
inputs:
  message:
    type: string
    inputBinding:
      position: 1
outputs:
  output_file:
    type: File
    outputBinding:
      glob: "*.txt"
stdout: "$(inputs.message)_stdout.log"
