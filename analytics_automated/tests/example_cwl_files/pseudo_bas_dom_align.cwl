# This is a manually created example file for the task in AAv1 called split_pdb_files
# example: 4 input, 0 parameter, 1 output
class: CommandLineTool
cwlVersion: v1.2
baseCommand: /home/dbuchan/Code/pGenTHREADER/bin/pseudo_bas_dom
arguments: ["-S", "-p", "-c11.0", "-C20", "-h0.2"]
requirements:
  - class: EnvVarRequirement
    envDef:
      THREAD_DIR: /home/dbuchan/Code/pGenTHREADER/data
      TDB_DIR: /home/dbuchan/Code/pGenTHREADER/cath_domain_tdb

inputs:
  input_ss2:
    type: File
    inputBinding:
      prefix: -F
      separate: false
      format: "https://github.com/psipred/psipred/ss2"
  input_mtx:
    type: File
    inputBinding:
      format: "http://edamontology.org/format_3916"
  input_pseudo:
    type: File
    inputBinding:
      format: "https://github.com/psipred/pGenTHREADER/pseudo"
  input_presults:
    type: File
    inputBinding:
      format: "https://github.com/psipred/pGenTHREADER/presults"

outputs:
  output_pdb:
    type: File
    outputBinding:
      glob: "*.align"

stdout: "$(inputs.input_file.basename).align"
