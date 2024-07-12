cwlVersion: v1.0

steps:
  step1:
    run: command.sh
    inputs:
      input_file:
        type: File
      parameter1:
        type: string
    outputs:
      output_file:
        type: File

requirements:
  class: DockerRequirement

labels:
  - label1

hints:
  softwareRequirements:
    - req1: value1