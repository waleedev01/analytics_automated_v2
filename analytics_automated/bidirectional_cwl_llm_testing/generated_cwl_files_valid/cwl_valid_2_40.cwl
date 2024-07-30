cwlVersion: v1.2
class: Workflow

inputs: []
outputs: []

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      file_input: input_file
    out:
      output_file: output_file

  step2:
    run: CommandLineTool2.cwl
    in:
      file_input: step1/output_file
    out:
      final_output: final_output

