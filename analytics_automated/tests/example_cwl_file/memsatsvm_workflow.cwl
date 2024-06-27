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

      baseCommand: [python, /home/dbuchan/Code/s4pred/run_model.py, --device, cpu, -t, ss2, -t2, horiz, -z, --outdir, ./, --prefix]

      stdout: "$(inputs.input_file.basename).bls"

      inputs:
        input_fasta_file:
          type: File
          format: "http://edamontology.org/format_1929"
          inputBinding:
            position: 14

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
