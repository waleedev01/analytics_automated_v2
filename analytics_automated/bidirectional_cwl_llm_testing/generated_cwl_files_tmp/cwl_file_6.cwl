cwlVersion: v1.0

class: CommandLineTool

inputs:

- id: input_file_1
  type: File

outputs:
- id: output_file
  type: File

requirements:
- class: DockerRequirement
  dockerPull: busybox

baseCommand: echo

stdout: output.txt