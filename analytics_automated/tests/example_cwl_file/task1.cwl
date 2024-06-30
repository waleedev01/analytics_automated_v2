cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  input1:
    type: string
    inputBinding:
      position: 1
outputs:
  output1:
    type: stdout
stdout: output.txt
requirements:
  - class: ShellCommandRequirement
  - class: EnvVarRequirement
    envDef:
      MY_VAR: "Hello World"
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input1)
  - class: SoftwareRequirement
    packages:
      - package: echo
        version: ["1.0"]
  - class: StepInputExpressionRequirement
successCodes: [0]
temporaryFailCodes: [1]
permanentFailCodes: [2]
AAIncompleteOutputsBehaviour: 2