cwlVersion: v1.0

InvalidWorkflow:
  class: Workflow

steps:
  step1:
    run: echo
    in:
      message: "Hello, world!"