cwlVersion: v1.2
class: Workflow
steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1.txt
    out: [output1]

  step2:
    run: CommandLineTool2.cwl
    in:
      input2: output1
    out: [output2]

baseCommand: ['echo', 'Hello, World']
inputs:
  input1: File

outputs:
  output2: File