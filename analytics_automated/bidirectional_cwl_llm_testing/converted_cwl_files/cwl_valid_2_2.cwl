cwlVersion: v1.2
class: Workflow
inputs:
  input_file:
    type: File
outputs:
  output_file_0:
    type: File
    outputSource: CommandLineTool/output_0
steps:
  CommandLineTool:
    run: CommandLineTool.cwl
    in:
      input_0: input_file
    out: []
  CommandLineTool2:
    run: CommandLineTool2.cwl
    in:
      input_0: input_file
    out: []
requirements: []
