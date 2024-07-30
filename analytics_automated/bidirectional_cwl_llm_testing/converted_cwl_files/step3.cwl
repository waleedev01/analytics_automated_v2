cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - step3.sh
  - $I1
inputs: {}
outputs:
  output_step3:
    type: File
    outputBinding:
      glob: '*.out'
