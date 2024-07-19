cwlVersion: v1.0

class: CommandLineTool

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

stdout: output.txt

baseCommand: cat

requirements:
  - class: DockerRequirement

steps:
  - id: step1
    run: some_script.sh
    in:
      input: input_file
    out:
      output: output_file