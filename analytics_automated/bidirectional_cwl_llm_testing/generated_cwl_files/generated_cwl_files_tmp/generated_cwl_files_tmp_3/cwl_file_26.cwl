cwlVersion: v1.0

# Missing 'class' field
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_file:
    type: File
    outputBinding:
      glob: $(inputs.input_file.basename)

# Missing 'class' field
steps:
  step1:
    run: command_tool.cwl
    in:
      input_file: input_file
    out:
      output_file: output_file