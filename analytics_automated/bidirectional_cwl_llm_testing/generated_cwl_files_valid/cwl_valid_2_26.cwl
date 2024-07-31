cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
    out:
      output_file: output_file

outputs:
  final_output:
    type: File
    outputBinding:
      glob: $(step1.output_file)