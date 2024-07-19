cwlVersion: v1.0

class: Workflow

requirements:
  - class: Step
    inputs:
      - id: input_file
        type: File
      - id: output_file
        type: File
    outputs:
      - id: output_file
        type: File

steps:
  step1:
    run: tool.cwl
    in:
      input_file: 
    out:
      output_file: 

metadata:
  name: Missing fields workflow