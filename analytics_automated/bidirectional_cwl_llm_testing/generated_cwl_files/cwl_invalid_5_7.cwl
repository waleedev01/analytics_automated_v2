cwlVersion: v1.0
class: CommandLineTool
outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: echo

# Missing 'inputs' section -