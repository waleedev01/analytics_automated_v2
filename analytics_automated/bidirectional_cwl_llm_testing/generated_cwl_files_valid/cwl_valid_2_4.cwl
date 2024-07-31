cwlVersion: v1.2
class: Workflow
inputs:
  input1:
    type: Any
    label: Input file 1
  input2:
    type: Any
    label: Input file 2
steps:
  step1:
    run: step1.cwl
    in:
      input1: input1
      input2: input2
    out: [output]
  step2:
    run: step2.cwl
    in:
      input: step1/output
outputs:
  final_output:
    type: Any
    outputSource: step2/output