cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
requirements:
  - class: EnvVarRequirement
    envDef:
      - envName: ANALYSIS_MODE
        envValue: "advanced"
hints:
  - class: SoftwareRequirement
    packages:
      - package: "createfasta"
        version: ["1.0"]
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
    format: "https://github.com/psipred/psipred/ss"
    inputBinding:
      position: 3
outputs:
  output1:
    type: File
    outputBinding:
      glob: "*.txt"
