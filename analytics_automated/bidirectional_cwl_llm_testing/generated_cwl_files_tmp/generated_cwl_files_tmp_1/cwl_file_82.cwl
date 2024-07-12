cwlVersion: v1.0

class: CommandLineTool

inputs:
  input_file:
    type: File
    label: input file

outputs:
  output_file:
    type: File
    label: output file

requirements:
  - class: DockerRequirement
    dockerPull: busybox

hints:
  - class
    sc: true

baseCommand: echo

arguments:
  - valueFrom: $(inputs.input_file.path)
    prefix: "Input file: "

stdout: $(inputs.output_file.path)