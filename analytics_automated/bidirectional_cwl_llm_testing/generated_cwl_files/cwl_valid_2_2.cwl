cwlVersion: v1.2
class: Workflow

inputs: {}
outputs: {}

steps:
  step1:
    run: commandlinetool.cwl
    in:
      input1: input_step1
    out:
      output1: output_step1

  step2:
    run: commandlinetool2.cwl
    in:
      input2: step1/output1
    out:
      output2: output_step2

baseCommand: []

File: commandlinetool.cwl
class: CommandLineTool
inputs: {}
outputs: {}
baseCommand: []

File: commandlinetool2.cwl
class: CommandLineTool
inputs: {}
outputs: {}
baseCommand: []