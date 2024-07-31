cwlVersion: v1.2
class: Workflow

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input1: input_file.txt
    out:
      output1: output_file.txt

  step2:
    run: AnotherCommandLineTool.cwl
    in:
      input2: step1/output1
    out:
      output2: final_output.txt

requirements:
  - class: CommandLineTool
    requirements:
      DockerRequirement:
        dockerPull: ubuntu:latest

inputs:
  input_file.txt:
    type: File
    inputBinding:
      position: 1

outputs:
  final_output.txt:
    type: File
    outputBinding:
      glob: $(inputs.input_file)