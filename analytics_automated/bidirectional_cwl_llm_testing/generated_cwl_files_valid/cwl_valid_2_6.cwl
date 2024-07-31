cwlVersion: v1.2
class: Workflow

inputs: []
outputs: []

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

  step3:
    run: CommandLineTool3.cwl
    in:
      input3: step2/output2.txt
    out:
      output3: final_output.txt

  step4:
    run: CommandLineTool4.cwl
    in:
      input4: step3/output3.txt
    out:
      output4: final_output2.txt