cwlVersion: v1.2
class: CommandLineTool
baseCommand: [bash, -c]
inputs:
  input1:
    type: string
    inputBinding:
      position: 1
  input2:
    type: string
    inputBinding:
      position: 2
outputs:
  output1:
    type: stdout
  output2:
    type: File
    outputBinding:
      glob: output_file.txt

