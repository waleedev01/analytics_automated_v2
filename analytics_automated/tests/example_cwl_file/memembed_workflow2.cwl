# This is a manually created example file for the task in AAv1 called memembed

class: Workflow
cwlVersion: v1.2

inputs:
  input_file: File

outputs:
  output_pdb:
    type: File
    outputSource: memembed2/output_pdb
  stdout_log:
    type: File
    outputSource: memembed2/stdout_log

steps:
  memembed2:
    run: memembed.cwl
    in:
      input_file: input_file
    out: 
      - output_pdb
      - stdout_log
