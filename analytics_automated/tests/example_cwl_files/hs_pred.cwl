cwlVersion: v1.2
class: CommandLineTool
baseCommand: /home/dbuchan/Code/hspred/bin/hs-pred_v0_1.pl
doc: run the hotspot prediction

arguments:
  - valueFrom: /home/dbuchan/Code/hspred/data
    position: 4

inputs:
  input_dir:
    type: Directory
    inputBinding:
      position: 5
    default:
      class: Directory
      location: $(runtime.tmpdir)
      listing:
        - class: File
          glob: "*.hb2"
        - class: File
          glob: "*.input"
  first_chain:
    type: string
    default: A
    inputBinding:
      position: 2
  second_chain:
    type: string
    default: B
    inputBinding:
      position: 3

outputs:
  output_ss:
    type: File
    outputBinding:
      glob: "*.out"

stdout: "*.stdout"
