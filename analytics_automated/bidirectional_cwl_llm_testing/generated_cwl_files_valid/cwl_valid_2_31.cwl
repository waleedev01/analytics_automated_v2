cwlVersion: v1.1
class: Workflow

inputs:
  input_file:
    type: File
    label: Input file

outputs:
  output_file:
    type: File
    label: Output file

steps:
  first_step:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
    out:
      - output_file

  second_step:
    run: 2ndCommandLineTool.cwl
    in:
      input_file: first_step/output_file
    out:
      - output_file
      - final_output

requirements:
  - class: CommandLineTool
    id: CommandLineTool.cwl
    cwlVersion: v1.1
    baseCommand: echo
    inputs:
      input_file:
        type: File
        inputBinding:
          prefix: --input
    outputs:
      output_file:
        type: File
        outputBinding:
          glob: output.txt

  - class: CommandLineTool
    id: 2ndCommandLineTool.cwl
    cwlVersion: v1.1
    baseCommand: cat
    inputs:
      input_file:
        type: File
        inputBinding:
          position: 1
    outputs:
      output_file:
        type: File
        outputBinding:
          glob: output.txt
      final_output:
        type: File
        outputBinding:
          glob: final_output.txt