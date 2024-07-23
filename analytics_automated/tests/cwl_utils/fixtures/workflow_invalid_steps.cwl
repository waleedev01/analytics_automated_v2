cwlVersion: v1.0
class: Workflow
inputs:
  input1:
    type: File
outputs:
  output1:
    type: File
    outputSource: some_tool_1/output
steps:
  step1:
    run:
      class: CommandLineTool
      baseCommand: echo
      requirements:
        - class: EnvVarRequirement
          envDef: 123
      stdout: "$(inputs.input_file.basename).stdout"
      inputs:
        input_file:
          type: File
      outputs:
        output1:
          type: stdout 
    in:
      input_file:
        source: input1
    out: output1
