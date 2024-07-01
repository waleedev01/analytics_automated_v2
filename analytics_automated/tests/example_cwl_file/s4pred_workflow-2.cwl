# This is a manually created example file for the task in AAv1 called memembed

class: Workflow
cwlVersion: v1.2

inputs:
  input_file: File

outputs:
  output_ss2:
    type: File
    outputSource: s4pred_run_model2/output_ss2
  output_horiz:
    type: File
    outputSource: s4pred_run_model2/output_horiz

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

  s4pred_run_model2:
    run:
      class: CommandLineTool

      baseCommand: [python, /home/dbuchan/Code/s4pred/run_model.py, --device, cpu, -t, ss2, -t2, horiz, -z, --outdir, ./, --prefix]

      stdout: "$(inputs.input_file.basename).stdout"

      inputs:
        input_file:
          type: File
          format: "http://edamontology.org/format_1929"
          inputBinding:
            position: 14

      outputs:
        output_ss2:
          type: File
          outputBinding:
            glob: "*.ss2"
        output_horiz:
          type: File
          outputBinding:
            glob: "*.horiz"
        
    in:
      input_file:
        source: create_fasta2/output_fasta

    out: 
      - output_ss2
      - output_horiz
