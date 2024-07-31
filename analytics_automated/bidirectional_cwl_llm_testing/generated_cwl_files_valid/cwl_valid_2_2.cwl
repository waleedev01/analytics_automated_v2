cwlVersion: v1.2
class: Workflow

inputs: {}
outputs: {}

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1_file
    out:
      output1: output1_file

  step2:
    run: CommandLineTool2.cwl
    in:
      input2: step1/output1
    out:
      output2: output2_file

baseCommand: []

CommandLineTool.cwl:
cwlVersion: v1.2
class: CommandLineTool

inputs:
  input1: File

outputs:
  output1: File

baseCommand: echo

CommandLineTool2.cwl:
cwlVersion: v1.2
class: CommandLineTool

inputs:
  input2: File

outputs:
  output2: File

baseCommand: echo