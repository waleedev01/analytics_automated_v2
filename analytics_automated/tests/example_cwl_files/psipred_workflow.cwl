cwlVersion: v1.0
class: Workflow

inputs:
  input-file:
    type: File
outputs:
  output-file:
    type: File
    outputSource: psipass2/output

steps:
  create_fasta2:
    run: create_fasta2.cwl
    in:
      input: input-file
    out: output
  run_legacy_psiblast2:
    run: run_legacy_psiblast2.cwl
    in:
      input: create_fasta2/output
    out: [output]
  psipred2:
    run: psipred2.cwl
    in:
      input: [run_legacy_psiblast2/output]
    out: output
  psipass2:
    run: psipass2.cwl
    in:
      input: psipred2/output
    out: [output]
