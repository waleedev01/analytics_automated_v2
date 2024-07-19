cwlVersion: v1.0
class: CommandLineTool

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: "--input-file"

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt
    type: String  # Incorrect type for output

baseCommand: cat