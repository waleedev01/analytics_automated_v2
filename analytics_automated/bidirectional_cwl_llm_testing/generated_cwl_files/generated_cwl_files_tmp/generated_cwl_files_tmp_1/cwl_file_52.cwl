cwlVersion: v1.0
class: CommandLineTool

inputs:
  - id: input_file
    type: File
    inputBinding:
      position: 1

outputs:
  - id: output_file
    type: File
    outputBinding:
      glob: output.txt

requirements:
  - class: ShellCommandRequirement

cmd: cat $(inputs.input_file) > output.txt