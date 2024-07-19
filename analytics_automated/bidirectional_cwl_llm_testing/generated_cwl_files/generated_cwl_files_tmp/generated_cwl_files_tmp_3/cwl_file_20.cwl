cwlVersion: v1.0

invalidStep:
  run: invalid_tool.cwl
  label: My Invalid Step
  inputs:
    - id: input_file
      type: File
  outputs:
    - id: output_file
      type: File