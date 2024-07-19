cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
requirements:
  - class: EnvVarRequirement
    envDef:
      MY_VAR: "example"
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: stdout