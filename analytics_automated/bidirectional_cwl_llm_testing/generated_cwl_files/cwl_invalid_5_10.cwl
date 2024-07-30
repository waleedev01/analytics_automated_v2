cwlVersion: v1.0
class: CommandLineTool
outputs:
  output_file:
    type: File
    outputBinding:
      glob: result.txt
baseCommand: echo
arguments:
  - valueFrom: "Hello, World!"