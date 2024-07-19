cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
outputs:
  - id: output_file
    type: File
    outputBinding:
      glob: output.txt
inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1
requirements:
  DockerRequirement:
    dockerPull: ubuntu:latest