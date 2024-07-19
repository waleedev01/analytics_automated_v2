cwlVersion: v1.0

InvalidWorkflow:
  class: Workflow

steps:
  step1:
    run: tool.cwl
    in:
      input: input1.txt

requirements:
  - class: Step
    step: step1