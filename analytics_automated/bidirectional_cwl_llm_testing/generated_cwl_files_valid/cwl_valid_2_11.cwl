cwlVersion: v1.2
class: Workflow

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

steps:
  job1:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
    out: 
      - output_file

  job2:
    run: AnotherCommandLineTool.cwl
    in:
      input_file: input_file
    out:
      - output_file