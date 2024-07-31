cwlVersion: v1.2
class: Workflow

inputs: []
outputs: []

steps:
  step1:
    run: CommandLineTool.cwl
    in: []
    out: []

  step2:
    run: AnotherCommandLineTool.cwl
    in: []
    out: []