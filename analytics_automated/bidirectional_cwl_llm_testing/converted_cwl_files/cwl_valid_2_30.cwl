cwlVersion: v1.2
class: Workflow
inputs:
  input-file:
    type: File
outputs:
  output-file:
    type: File
    outputSource: CommandLineTool/output
steps:
  CommandLineTool:
    run: CommandLineTool.cwl
    in:
      input: input-file
    out: []
  another_tool:
    run: another_tool.cwl
    in:
      input: CommandLineTool/output
    out: []
