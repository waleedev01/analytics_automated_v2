cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs: 
  input_message: 
    type: string
    inputBinding:
      position: 1
      prefix: ""
outputs:
  output_message:
    type: string
    outputBinding:
      glob: "output.txt"