cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File
outputs:
  output_file_0:
    type: File
    outputSource: step1_tool/output_0
steps:
  step1_tool:
    run: step1_tool.cwl
    in:
      input_0: input_file
    out:
      - output_0
  step2_tool:
    run: step2_tool.cwl
    in:
      input_0: input_file
    out: []
requirements: []
