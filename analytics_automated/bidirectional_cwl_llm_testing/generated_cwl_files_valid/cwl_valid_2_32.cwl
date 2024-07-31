cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
    out:
      output_file: output_file

  step2:
    run: AnotherCommandLineTool.cwl
    in:
      input_file: step1.output_file
    out:
      output_file: output_file