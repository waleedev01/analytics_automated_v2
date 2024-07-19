cwlVersion: v1.0
class: CommandLineTool

inputs:
  infile:
    type: File

outputs:
  outfile:
    type: File

arguments:
  - valueFrom: $(inputs.infile.path)

requirements:
  - class: DockerRequirement

stdout: output.txt

baseCommand: echo

# missing required fields like inputs and outputs