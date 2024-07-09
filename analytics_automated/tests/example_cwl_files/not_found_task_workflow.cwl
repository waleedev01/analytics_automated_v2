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
    outputSource: task12345/output1

steps:
  task12345:
    run: task12345.cwl
    in:
      input1: input-wf
    out: [output1]
