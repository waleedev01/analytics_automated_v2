class: CommandLineTool

requirements:
  - class: DockerRequirement

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: string

steps:
  - run: echo "Hello, world!"
    inputs:
      input: input_file
    outputs:
      output: output_file