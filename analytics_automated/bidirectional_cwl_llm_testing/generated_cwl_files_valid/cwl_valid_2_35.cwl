cwlVersion: v1.2
class: Workflow

inputs:
  - id: input_file
    type: File

steps:
  step1:
    run: tool.cwl
    in:
      input_file: input_file
    out:
      - id: output_file
        type: File

outputs:
  final_output:
    outputSource: step1/output_file

requirements:
  - class: CommandLineTool
    requirements:
      - class: InlineJavascriptRequirement

  - class: DockerRequirement
    dockerPull: ubuntu:latest