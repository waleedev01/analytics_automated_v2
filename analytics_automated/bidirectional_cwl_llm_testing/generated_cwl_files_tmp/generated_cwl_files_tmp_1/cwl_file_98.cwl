cwlVersion: v1.0

attr1: 
  type: string
  label: "Attribute 1"

process:
  run: test.sh
  inputs:
    attr1: 
      type: string

requirements:
  DockerRequirement:
    dockerPull: ubuntu:latest

class: CommandLineTool