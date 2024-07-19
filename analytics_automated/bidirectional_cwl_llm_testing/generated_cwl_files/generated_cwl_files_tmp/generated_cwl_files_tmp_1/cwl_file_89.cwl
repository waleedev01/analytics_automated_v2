cwlVersion: v1.0
class: CommandLineTool
baseCommand: cat
inputs:
  - id: input_file
    type: File
    label: Input file
outputs:
  - id: output_file
    type: File
    label: Output file
    outputBinding:
      glob: output.txt