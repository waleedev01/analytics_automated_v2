cwlVersion: v1.0
class: CommandLineTool
baseCommand: [/home/dbuchan/Code/psipred/bin/psipred, /home/dbuchan/Code/psipred/data/weights.dat, /home/dbuchan/Code/psipred/data/weights.dat2, /home/dbuchan/Code/psipred/data/weights.dat3]

inputs:
  input_mtx_file:
    type: File
    format: "http://edamontology.org/format_3916"
    inputBinding:
      position: 2

outputs:
  output_ss:
    type: File
    outputBinding:
      glob: "*.ss"

stdout: "$(inputs.input_file.basename).ss"
