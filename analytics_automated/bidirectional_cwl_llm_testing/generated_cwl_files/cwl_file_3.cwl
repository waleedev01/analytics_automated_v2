cwlVersion: v1.0
id: my_workflow
inputs:
  input_file:
    type: File
    label: "Input file"
outputs:
  output_file:
    type: File
    outputBinding:
      glob: "$(inputs.input_file.basename)"
steps:
  step1:
    run: tool.cwl
    in:
      input: input_file
    out:
      - output: output_file