cwlVersion: v1.0

class: CommandLineTool

label: A sample CWL file with missing required fields

hints:
  - class: DockerRequirement
    dockerPull: ubuntu:latest

inputs:
  input1:
    type: File
    label: Input file

outputs:
  output1:
    type: File
    label: Output file

stdout: output.txt

baseCommand: echo

arguments:
  - valueFrom: $(inputs.input1.path)