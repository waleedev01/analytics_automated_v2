cwlVersion: v1.0

class: CommandLineTool

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename)

requirements:
  - class: DockerRequirement
    dockerPull: busybox

arguments:
  - valueFrom: $(inputs.input_file)

baseCommand: echo