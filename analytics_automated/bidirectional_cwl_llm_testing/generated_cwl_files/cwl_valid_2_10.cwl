cwlVersion: v1.2
class: Workflow
steps:
  step1:
    run: step1.cwl
    in:
      input1: file
    out:
      output1: file

  step2:
    run: step2.cwl
    in:
      input2: File
    out:
      output2: File

inputs: {}
outputs: {}