cwlVersion: v1.0

invalid_field: missing_required_fields

inputs:
  - id: input_file
    type: File

outputs:
  - id: output_file
    type: File

steps:
  - id: step1
    run:
      class: CommandLineTool
      baseCommand: echo
      inputs:
        - id: input
          type: File
          inputBinding:
            position: 1
      outputs:
        - id: output
          type: File
          outputBinding:
            glob: $(inputs.input.basename).txt
    in:
      input: input_file
    out:
      output: output_file