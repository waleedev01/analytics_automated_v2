cwlVersion: v1.2
class: Workflow

inputs: {}
outputs: {}

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      - id: input1
        source: input1
    out: []

  step2:
    run: CommandLineTool2.cwl
    in:
      - id: input2
        source: step1/output
    out: []

  step3:
    run: CommandLineTool3.cwl
    in:
      - id: input3
        source: step2/output
    out: []