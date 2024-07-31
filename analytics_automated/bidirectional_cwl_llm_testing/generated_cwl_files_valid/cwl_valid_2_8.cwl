cwlVersion: v1.2
class: Workflow

inputs: {}
outputs: {}

steps:
  step1:
    run: /path/to/step1.cwl
    in:
      input1: step1/input1
      input2: step1/input2
    out: 
      output1: step1/output1

  step2:
    run: /path/to/step2.cwl
    in:
      input1: step2/input1
      input2: step2/input2
    out: 
      output1: step2/output1

requirements:
  - class: CommandLineTool
    loadContents: true

hints:
  DockerRequirement:
    dockerPull: ubuntu:latest