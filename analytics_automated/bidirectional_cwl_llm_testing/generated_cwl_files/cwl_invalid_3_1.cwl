cwl:
  class: CommandLineTool
  cwlVersion: missing

  inputs:
    input_file:
      type: File
      inputBinding:
        position: 1

  outputs:
    output_file:
      type: File
      outputBinding:
        glob: "*.out"

  baseCommand: echo "Hello, world!"