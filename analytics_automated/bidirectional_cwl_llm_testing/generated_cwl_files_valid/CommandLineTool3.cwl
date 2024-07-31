class: CommandLineTool
cwlVersion: v1.2
baseCommand: echo

inputs:
  inputFile:
    type: File
    inputBinding:
      position: 1

outputs:
  outputMessage:
    type: stdout

requirements:
  InlineJavascriptRequirement: {}

hints:
  DockerRequirement:
    dockerImageId: alpine:latest

label: CommandLineTool3
doc: A simple echo command tool

id: CommandLineTool3.cwl