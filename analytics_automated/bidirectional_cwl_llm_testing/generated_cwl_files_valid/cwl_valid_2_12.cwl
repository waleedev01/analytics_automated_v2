cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: --input

outputs:
  output_file:
    type: File
    outputBinding:
      glob: "output.txt"

steps:
  step1:
    run: step1.cwl
    in:
      input_file: input_file
    out:
      - output_file

  step2:
    run: step2.cwl
    in:
      input_file: step1/output_file
    out:
      - output_file

requirements:
  - class: CommandLineTool
    id: step1
    baseCommand: ["cat"]
    inputs:
      input_file:
        type: File
      outputs:
        output_file:
          type: File
          outputBinding:
            glob: "output.txt"

  - class: CommandLineTool
    id: step2
    baseCommand: ["grep"]
    inputs:
      input_file:
        type: File
      outputs:
        output_file:
          type: File
          outputBinding:
            glob: "output.txt"