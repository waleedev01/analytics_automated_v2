cwlVersion: v1.0
class: CommandLineTool

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

requirements:
  - class: DockerRequirement
    dockerImageId: busybox
    dockerPull: busybox

arguments:
  - valueFrom: $(inputs.input_file)
    position: 1

baseCommand: echo

hints:
  - class: ShellCommandRequirement

  - class: ResourceRequirement
    ramMin: 100MB