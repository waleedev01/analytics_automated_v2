cwlVersion: v1.0

class: CommandLineTool

label: Example tool

inputs:
  - id: input_file
    type: File
    label: Input file

outputs:
  - id: output_file
    type: File
    label: Output file

requirements:
  - class: DockerRequirement
    dockerImageId: alpine:3.9

hints:
  - class: ShellCommandRequirement

stdout: output.txt

baseCommand: cat

arguments: ["$(inputs.input_file.path)"]

$("outputs.output_file"):
  path: output.txt