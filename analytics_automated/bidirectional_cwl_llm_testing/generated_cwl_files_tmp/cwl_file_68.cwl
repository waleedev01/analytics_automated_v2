cwlVersion: v1.0
class: CommandLineTool

inputs:
  inputFile:
    type: File

outputs:
  outputFile:
    type: File

baseCommand: cat

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:latest

hints:
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 1000MB