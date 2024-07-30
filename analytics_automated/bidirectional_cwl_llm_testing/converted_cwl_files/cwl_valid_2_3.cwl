cwlVersion: v1.2
class: Workflow
inputs:
  input-file:
    type: File
outputs:
  output-file:
    type: File
    outputSource: my_command_tool/output
steps:
  my_command_tool:
    run: my_command_tool.cwl
    in:
      input: input-file
    out: []
  my_next_command_tool:
    run: my_next_command_tool.cwl
    in:
      input: my_command_tool/output
    out:
      - output
