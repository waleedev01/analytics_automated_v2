cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - script.sh
  - --input
  - $I1
inputs: {}
outputs:
  output_script:
    type: File
    outputBinding:
      glob: '*.txt'
