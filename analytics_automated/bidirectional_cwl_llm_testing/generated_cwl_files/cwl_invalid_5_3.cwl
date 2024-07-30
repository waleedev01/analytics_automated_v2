cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
outputs:
  - id: output_file
    type: stdout
    outputBinding:
      glob: output.txt