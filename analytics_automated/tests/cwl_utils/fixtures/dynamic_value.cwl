# This is a manually created example file for the task in AAv1 called split_pdb_files
# example: 1 input, 2 parameter, 1 output
class: CommandLineTool
cwlVersion: v1.2
baseCommand: echo
arguments:
  - valueFrom: "$ID"
    position: 1
  - valueFrom: "$(runtime.tmpdir)/$ID/$(inputs.input_file.basename)"
  - valueFrom: "$O1"

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      format: ".out"

outputs:
  output_pdb:
    type: File
    outputBinding:
      glob: "*.txt"

stdout: "$(inputs.input_file.basename).stdout"
