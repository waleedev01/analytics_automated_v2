cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1.txt
    out:
      output1: output1.txt

  step2:
    run: CommandLineTool2.cwl
    in:
      input2: input2.txt
    out:
      output2: output2.txt

CommandLineTool.cwl:
cwlVersion: v1.2
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

CommandLineTool2.cwl:
cwlVersion: v1.2
class: CommandLineTool

baseCommand: echo

inputs:
  input2:
    type: string
    inputBinding:
      position: 1

outputs:
  output2:
    type: stdout