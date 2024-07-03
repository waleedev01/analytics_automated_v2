cwlVersion: v1.0
class: Workflow
requirements:
  - class: EnvVarRequirement
    envDef:
      WORKFLOW_VAR: example_value

inputs:
  input-wf:
    type: File

outputs:
  output-wf:
    type: File
    outputSource: task1/output1

steps:
  task1:
    run:
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
            THREAD_DIR: "/home/dbuchan/Code/pGenTHREADER/data"
            HELLO: $(inputs.input1)
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
    in:
      input1: input-wf
    out: [output1]
