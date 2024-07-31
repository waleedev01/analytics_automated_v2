cwlVersion: v1.2
class: Workflow

inputs: {}
outputs: {}

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1.txt
    out:
      output1: output1.txt

  step2:
    run: CommandLineTool2.cwl
    in:
      input2: step1/output1.txt
    out:
      output2: output2.txt