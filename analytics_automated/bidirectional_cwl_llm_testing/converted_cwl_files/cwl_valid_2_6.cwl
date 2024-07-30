cwlVersion: v1.2
class: Workflow
inputs:
  input-file:
    type: File
outputs:
  output-file:
    type: File
    outputSource: step1_tool/output
steps:
  step1_tool:
    run: step1_tool.cwl
    in:
      input: input-file
    out:
      - output
  step2_tool:
    run: step2_tool.cwl
    in:
      input: step1_tool/output
    out: []
