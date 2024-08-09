cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
hints:
  - class: SoftwareRequirement
    packages:
      package: "createfasta"
      version: ["1.0"]
inputs:
  input1:
    type: File
    inputBinding:
      position: 1
outputs:
  output1:
    type: File
    outputBinding:
      glob: "*.txt"
