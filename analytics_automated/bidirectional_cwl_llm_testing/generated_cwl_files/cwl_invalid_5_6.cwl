cwlVersion: v1.0
class: CommandLineTool
outputs:
  result:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: echo "Hello, World!"