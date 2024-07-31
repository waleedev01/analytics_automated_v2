cwlVersion: v1.2
class: Workflow

inputs:
  input1: File
  input2: string

outputs:
  output1: File
  output2: string

steps:
  step1:
    run: step1_tool.cwl
    in:
      input_file: input1
    out:
      output_file: output1
  step2:
    run: step2_tool.cwl
    in:
      input_string: input2
    out:
      output_string: output2

requirements:
  - class: CommandLineTool
    requirements:
      - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: docker/centos

hints:
  DockerRequirement:
    dockerImageId: docker/centos:latest