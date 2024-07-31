cwlVersion: v1.2
class: Workflow

inputs: []
outputs: []

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1_value
    out:
      output1: output1.txt

  step2:
    run: CommandLineTool2.cwl
    in:
      input2: input2_value
    out:
      output2: output2.txt

  step3:
    run: CommandLineTool3.cwl
    in:
      input3: input3_value
    out:
      output3: output3.txt