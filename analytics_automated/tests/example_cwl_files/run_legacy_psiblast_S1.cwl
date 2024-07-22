cwlVersion: v1.0
class: CommandLineTool
baseCommand: [python, /home/dbuchan/Code/blast_cache/scripts/run_legacy_blast.py, $TMP/$ID, http://127.1.2.1, /home/dbuchan/Applications/blast-2.2.26/bin, /home/dbuchan/Data/uniref_test_db/uniref_test.fasta, chk, -b, 0, -j, 3, -h, 0.001, -v, 5000]

inputs:
  input_fasta_file:
    type: File
    format: "http://edamontology.org/format_1929"
    inputBinding:
      position: 2

outputs:
  output_mtx:
    type: File
    outputBinding:
      glob: "*.mtx"
  output_chk:
    type: File
    outputBinding:
      glob: "*.chk"

AAConfiguration:
  - name: psiblast
    type: Software
    parameters: "-b 0 -j 3 -h 0.001 -v 5000"
    version: 2.23.2
  - name: uniref90
    type: Dataset
    version: 2023

stdout: "$(inputs.input_file.basename).bls"
