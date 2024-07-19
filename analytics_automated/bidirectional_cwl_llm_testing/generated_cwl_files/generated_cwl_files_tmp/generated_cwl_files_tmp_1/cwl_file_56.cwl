cwlVersion: v1.0

# missing required fields

# tool definition
cwlVersion: v1.0
class: CommandLineTool

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

baseCommand: echo 

stdout: output.txt