# This is a manually created example file for the task in AAv1 called split_pdb_files
# example: 1 input, 2 parameter, 1 output
class: CommandLineTool
cwlVersion: v1.2
baseCommand: /home/dbuchan/Code/hspred/bin/split_pdb.pl
arguments:
  - valueFrom: "$ID"
  - valueFrom: "$(runtime.tmpdir)/$ID"

inputs:
  first_chain:
    type: string
    default: "A"
    inputBinding:
      position: 2
      separate: false
  second_chain:
    type: string
    default: "B"
    inputBinding:
      position: 3
      separate: false
  input_file:
    type: File
    inputBinding:
      position: 1
      format: ".out"

outputs:
  output_pdb:
    type: File
    outputBinding:
      glob: "*.pdb"

stdout: "$(inputs.input_file.basename).stdout"
