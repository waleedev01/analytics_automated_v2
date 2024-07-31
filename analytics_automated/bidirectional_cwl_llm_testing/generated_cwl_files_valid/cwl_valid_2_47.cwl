cwlVersion: v1.2
class: Workflow

inputs:
  input1:
    type: Any
    inputBinding:
      position: 1

  input2:
    type: Any
    inputBinding:
      position: 2

outputs:
  output:
    type: Any

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1
      input2: input2
    out:
      - output

  step2:
    run: AnotherCommandLineTool.cwl
    in:
      input: step1/output
    out:
      - output