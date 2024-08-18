cwlVersion: v1.2
class: CommandLineTool
baseCommand: [bash, "-c"]
inputs:
  input_string:
    type: string
    inputBinding:
      position: 1

  output_file:
    type: File
    inputBinding:
      position: 2

outputs:
  reversed_string:
    type: File
    outputBinding:
      glob: "reversed_string.txt"


