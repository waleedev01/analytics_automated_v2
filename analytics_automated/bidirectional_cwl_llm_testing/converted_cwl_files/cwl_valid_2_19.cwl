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
  CommandLineTool2:
    run: CommandLineTool2.cwl
    in:
      input: CommandLineTool/output
    out: []
