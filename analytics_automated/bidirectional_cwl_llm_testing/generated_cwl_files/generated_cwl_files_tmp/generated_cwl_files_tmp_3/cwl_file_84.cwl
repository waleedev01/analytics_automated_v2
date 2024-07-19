cwlVersion: v1.0
class: CommandLineTool

inputs:
  input_data:
    type: File

outputs:
  output_data:
    type: File

args:
  - echo "Hello, World!" 

requirements:
  class: DockerRequirement
  dockerPull: ubuntu:latest