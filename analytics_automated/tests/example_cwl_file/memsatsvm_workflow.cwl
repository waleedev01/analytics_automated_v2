# This is a manually created example file for the task in AAv1 called memembed

class: Workflow
cwlVersion: v1.2

inputs:
  input_file: File
  input_fasta_file: File

outputs:
  output_mtx:
    type: File
    outputSource: run_legacy_psiblast2/output_mtx
  output_chk:
    type: File
    outputSource: run_legacy_psiblast2/output_chk

steps:
  create_fasta2:
    run:
      class: CommandLineTool

      baseCommand: [python, /home/dbuchan/Code/bioserf/bin/make_fasta.py]

      stdout: "$(inputs.input_file.basename).fasta"

      inputs:
        input_file:
          type: File
          inputBinding:
            position: 3

      outputs:
        output_fasta:
          type: File
          outputBinding:
            glob: "*.fasta"
        
    in:
      input_file: input_file
    out: 
      - output_fasta

  run_legacy_psiblast2:
    run:
      class: CommandLineTool

      baseCommand: [python, /home/dbuchan/Code/blast_cache/scripts/run_legacy_blast.py, $TMP/$ID, http://127.1.2.1, /home/dbuchan/Applications/blast-2.2.26/bin, /home/dbuchan/Data/uniref_test_db/uniref_test.fasta, chk, -b, 0, -j, 3, -h, 0.001, -v, 5000]

      stdout: "$(inputs.input_file.basename).bls"

      inputs:
        input_fasta_file:
          type: File
          format: "http://edamontology.org/format_1929"
          inputBinding:
            position: 3

      outputs:
        output_mtx:
          type: File
          outputBinding:
            glob: "*.mtx"
        output_chk:
          type: File
          outputBinding:
            glob: "*.chk"
        
    in:
      input_fasta_file: input_fasta_file

    out: 
      - output_mtx
      - output_chk
