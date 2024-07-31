cwlVersion: v1.2
class: Workflow

inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1

outputs:
  - id: output_file
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename)

steps:
  step1:
    run: command_tool.cwl
    in:
      input_file: input_file
    out:
      - output: output_file

  step2:
    run: another_command_tool.cwl
    in:
      input_file: step1/output
    out:
      - output: output_file