cwlVersion: v1.0
class: Workflow
requirements:
  - class: EnvVarRequirement
    envDef:
      WORKFLOW_VAR: example_value

outputs:
  output-wf:
    type: File
    outputSource: task1/output1

steps:
  task1:
    run: task1.cwl
    in:
      input1: input-wf
    out: [output1]
