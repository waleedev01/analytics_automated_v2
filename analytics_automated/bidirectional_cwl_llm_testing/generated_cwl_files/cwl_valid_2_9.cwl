cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_param1: input_file
    out:
      output_param1: output_file

  step2:
    run: AnotherCommandLineTool.cwl
    in:
      input_param2: step1/output_file
    out:
      output_param2: final_output

  step3:
    run: FinalCommandLineTool.cwl
    in:
      input_param3: step2/final_output
    out:
      output_param3: final_result