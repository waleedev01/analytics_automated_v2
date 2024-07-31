cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: tool.cwl
    in:
      input1: inputfile.txt
    out:
      output1: outputfile.txt

  step2:
    run: tool2.cwl
    in:
      input2: step1/output1
    out:
      output2: final_output.txt

inputs: {}

outputs: {}