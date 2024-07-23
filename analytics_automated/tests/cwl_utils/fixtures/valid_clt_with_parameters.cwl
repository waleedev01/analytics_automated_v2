cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
requirements:
  - class: EnvVarRequirement
    envDef:
      - envName: ANALYSIS_MODE
        envValue: "advanced"
inputs:
  parameter_1:
    type: string
    default: "0"
    inputBinding:
      position: 1
      prefix: -s
  parameter_2:
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: -b
  input_file:
    type: File
    inputBinding:
      position: 3
outputs:
  output1:
    type: File
    outputBinding:
      glob: "*.txt"
