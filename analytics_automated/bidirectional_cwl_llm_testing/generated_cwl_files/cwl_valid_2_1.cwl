cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: my_tool.cwl
    in:
      input1: input_file.txt
    out:
      output1: output_file.txt

  step2:
    run: my_tool2.cwl
    in:
      input2: steps.step1.output.output1
    out:
      output2: output_final.txt

  step3:
    run: my_tool3.cwl
    in:
      input3: steps.step2.output.output2
    out:
      output3: final_output.txt

inputs: []

outputs: []