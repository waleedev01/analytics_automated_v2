# This is a manually created example file for the task in AAv1 called memembed
# example: 1 input, 3 parameter, 2 output
class: CommandLineTool
cwlVersion: v1.2
baseCommand: /home/dbuchan/Code/bin/memembed

inputs:
  memembed_algorithm:
    type: string
    default: "0"
    inputBinding:
      position: 1
      prefix: -s
  memembed_barrel:
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: -b
  memembed_termini:
    type: string
    default: "in"
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
      glob: "$(inputs.input_file.basename).stdout"

stdout: "$(inputs.input_file.basename).stdout"
