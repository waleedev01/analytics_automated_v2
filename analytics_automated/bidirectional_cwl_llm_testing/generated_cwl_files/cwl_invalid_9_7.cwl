cwlVersion: v1.0
class: CommandLineTool
requirements:
  - StepRequirement
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt
baseCommand: cat