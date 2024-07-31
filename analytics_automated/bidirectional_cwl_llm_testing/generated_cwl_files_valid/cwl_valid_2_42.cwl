cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename).out

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
    out:
      output_file: output_file