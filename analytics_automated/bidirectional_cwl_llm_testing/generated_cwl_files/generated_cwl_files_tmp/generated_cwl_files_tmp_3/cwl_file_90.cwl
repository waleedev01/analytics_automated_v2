cwlVersion: v1.0

class: CommandLineTool

inputs:
  - id: input_file
  type: File
    doc: The input file to be processed

outputs:
  - id: output_file
  type: File
    doc: The output file

requirements:
  - class: ShellCommandRequirement

stdout: output.txt

baseCommand: echo

arguments:
  - valueFrom: $(inputs.input_file.path) > $(outputs.output_file.path)