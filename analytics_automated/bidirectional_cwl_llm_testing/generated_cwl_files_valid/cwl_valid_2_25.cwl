cwlVersion: v1.2
class: Workflow

hints:
  ScatterFeatureRequirement:
    scatterMethod: dotproduct

steps:
  step1:
    run: step1.cwl
    in:
      input1: input1.txt
    out:
      output1: output1.txt

  step2:
    run: step2.cwl
    in:
      input2: step1/output1.txt
    out:
      output2: output2.txt

inputs: {}
outputs: {}