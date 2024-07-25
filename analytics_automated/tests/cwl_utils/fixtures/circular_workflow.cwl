cwlVersion: v1.0
class: Workflow

inputs:
  input-wf:
    type: File
outputs:
  output-wf:
    type: File
    outputSource: some_tool_2/output

steps:
  some_tool_1:
    run:
      class: CommandLineTool
      baseCommand: echo
      stdout: "$(inputs.input_file.basename).stdout"
      inputs:
        input_file:
          type: File
      outputs:
        output1:
          type: stdout 
    in:
      input_file:
        source: some_tool_2/output1
    out: output1

  some_tool_2:
    run:
      class: CommandLineTool
      baseCommand: ls
      stdout: "$(inputs.input_file.basename).stdout"
      inputs:
        input_file:
          type: File
      outputs:
        output1:
          type: stdout 
    in:
      input_file:
        source: some_tool_1/output1
    out: output1