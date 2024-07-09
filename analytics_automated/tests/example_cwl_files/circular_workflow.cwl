cwlVersion: v1.0
class: Workflow

inputs:
  input-wf:
    type: File
outputs:
  output-wf:
    type: File
    outputSource: task4/report

steps:
  task1:
    run: task1.cwl
    in:
      input1: input-wf
    out: [output1]
  task2:
    run: task2.cwl
    in:
      input1: task3/output1
    out: [output1]
  task3:
    run: task3.cwl
    in:
      files: [task2/output1]
      mode: "analyze"
    out: [output1]
  task4:
    run: task4.cwl
    in:
      config: task1/output1
    out: [report]