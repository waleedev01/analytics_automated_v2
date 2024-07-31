cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: step1.cwl
    in:
      input1: step1_inputFile.txt
    out: [output1]

  step2:
    run: step2.cwl
    in:
      input2: step2_inputFile.txt
    out: [output2]

inputs: {}

outputs: {}