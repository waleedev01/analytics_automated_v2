cwlVersion: v1.2
class: Workflow

inputs:
  input_directory:
    type: Directory
    inputBinding:
      position: 1
  reference_file:
    type: File
    inputBinding:
      position: 2

outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_directory.basename).txt

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_file: input_directory/input.txt
      reference: reference_file
    out: [output_file]

  step2:
    run: AnotherCommandLineTool.cwl
    in:
      input_data: step1/output_file
    out: [final_output]

baseCommand: echo