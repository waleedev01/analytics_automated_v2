cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: step1.cwl
    in:
      input1: input1_file.txt
      input2: input2_file.txt
    out:
      output1: output1_file.txt

  step2:
    run: step2.cwl
    in:
      input3: steps.step1.output1
    out:
      output2: output2_file.txt

inputs: {}

outputs: {}