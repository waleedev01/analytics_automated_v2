cwlVersion: v1.2
class: Workflow

inputs: {}

outputs: {}

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input1_file
      input2: input2_file
    out:
      output: output_file

  step2:
    run: CommandLineTool2.cwl
    in:
      input3: input3_file
      input4: input4_file
    out:
      output: output_file

  step3:
    run: CommandLineTool3.cwl
    in:
      input5: input5_file
      input6: input6_file
    out:
      output: output_file