cwlVersion: v1.0
class: CommandLineTool
baseCommand: [python, /home/dbuchan/Code/bioserf/bin/make_fasta.py]
hints:
  - class: SoftwareRequirement
    packages:
      createfasta:
        version: ["1.0"]

inputs:
  input_file:
    type: File
    inputBinding:
      position: 2

outputs:
  output_fasta:
    type: File
    outputBinding:
      glob: "*.fasta"

stdout: "$(inputs.input_file.basename).fasta"
