cwlVersion: v1.1

class: CommandLineTool

description: This is an example of an invalid CWL file with missing required fields.

inputs:
  - id: input_file
    type: File
  - id: input_param
    type: string

outputs:
  - id: output_file
    type: File

requirements:
  - class: DockerRequirement

cmd: echo "Hello, world!" > output.txt

label: Missing required fields CWL file