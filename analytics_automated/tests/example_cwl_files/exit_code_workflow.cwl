class: Workflow
cwlVersion: v1.0

inputs:
  input_file:
    type: File

outputs:
  outputs:
    type: File
    outputSource: exit_code/output_fasta

steps:
  exit_code:
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

      successCodes: [100, 50]
      temporaryFailCodes: [1]
      permanentFailCodes: [128, 200]

    in:
      input_file: input_file
    out: 
      - output_fasta