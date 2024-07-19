steps:
  - id: step1
    run: script.sh
    inputs:
      message: string

inputs:
  message:
    type: string

outputs:
  output_message:
    type: string

requirements:
  DockerRequirement:
    dockerPull: ubuntu:latest