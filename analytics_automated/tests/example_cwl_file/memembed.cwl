# This is a manually created example file for the task in AAv1 called memembed
class: CommandLineTool
cwlVersion: v1.2
baseCommand: /home/dbuchan/Code/bin/memembed

inputs:
  memembed_algorithm:
    type: string
    inputBinding:
      position: 1
      prefix: -s
  memembed_barrel:
    type: boolean
    inputBinding:
      position: 2
      prefix: -b
  memembed_termini:
    type: string
    inputBinding:
      position: 3
      prefix: -n
  input_file:
    type: File
    inputBinding:
      position: 4

outputs:
  output_pdb:
    type: File
    outputBinding:
      glob: "*.pdb"
  stdout_log:
    type: File
    outputBinding:
      glob: "*.stdout"

stdout: $(inputs.input_file.basename).stdout
