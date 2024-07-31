cwlVersion: v1.2
class: Workflow

inputs: {}
outputs: {}

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: step1_input1
    out:
      - step1_output1

  step2:
    run: CommandLineTool.cwl
    in:
      input2: step2_input2
    out:
      - step2_output2

  step3:
    run: CommandLineTool.cwl
    in:
      input3: step3_input3
    out:
      - step3_output3

CommandLineTool.cwl:
cwlVersion: v1.2
class: CommandLineTool

baseCommand: echo

inputs:
  input1:
    type: string
    inputBinding:
      position: 1

  input2:
    type: string
    inputBinding:
      position: 1

  input3:
    type: string
    inputBinding:
      position: 1

outputs:
  - id: step1_output1
    type: string

  - id: step2_output2
    type: string

  - id: step3_output3
    type: string