cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File
outputs:
  output_file_0:
    type: File
    outputSource: my_command_tool/output_0
steps:
  my_command_tool:
    run: my_command_tool.cwl
    in:
      input_0: input_file
    out: []
  my_next_command_tool:
    run: my_next_command_tool.cwl
    in:
      input_0: input_file
    out:
      - output_0
requirements: []
