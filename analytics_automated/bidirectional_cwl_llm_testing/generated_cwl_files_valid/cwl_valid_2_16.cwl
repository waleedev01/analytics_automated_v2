cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
  input_dir:
    type: Directory
    inputBinding:
      prefix: --dir

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
      input_dir: input_dir
    out:
      - output_file

  step2:
    run: AnotherCommandLineTool.cwl
    in:
      input_file: step1/output_file
      input_dir: input_dir
    out:
      - output_file