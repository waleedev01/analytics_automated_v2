cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: script.cwl
    in:
      input1: input1.txt
    out:
      - output1.txt

  step2:
    run: script2.cwl
    in:
      input2: step1/output1.txt
    out:
      - output2.txt

inputs: {}

outputs: {}