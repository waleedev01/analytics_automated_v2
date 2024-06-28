cwlVersion: v1.0
class: CommandLineTool
baseCommand: [/home/dbuchan/Code/psipred/bin/psipass2, /home/dbuchan/Code/psipred/data/weights_p2.dat, 1, 1.0, 1.0]

inputs:
  input_ss_file:
    type: File
    format: "http://edamontology.org/format_3310"
    inputBinding:
      position: 7

outputs:
  output_ss2:
    type: File
    outputBinding:
      glob: "*.ss2"
  output_horiz:
    type: File
    outputBinding:
      glob: "*.horiz"
      position: 6

stdout: "$(inputs.input_file.basename).horiz"
