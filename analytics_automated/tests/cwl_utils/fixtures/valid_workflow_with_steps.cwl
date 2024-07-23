cwlVersion: v1.0
class: Workflow
inputs:
  input1:
    type: File
outputs:
  output1:
    type: File
    outputSource: step1/output
requirements:
  - class: EnvVarRequirement
    envDef:
      WORKFLOW_VAR: example_value
steps:
  some_tool_1:
    run:
      class: CommandLineTool
      baseCommand: echo
      requirements:
        - class: EnvVarRequirement
          envDef:
            WORKFLOW_VAR: example_value
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
      input_file: some_tool_1/output1
    out: output1
  
  some_tool_3:
    run:
      class: CommandLineTool
      baseCommand: mkdir
      stdout: "$(inputs.input_file.basename).stdout"
      inputs:
        input_file_1:
          type: File
        input_file_2:
          type: File
      outputs:
        output1:
          type: stdout 
    in: 
      input_file_1: [some_tool_1/output1, some_tool_2/output1]
      input_file_2: some_tool_2/output1
    out: output1
