cwlVersion: v1.2
class: CommandLineTool

baseCommand: bash

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  processed_files:
    type: File
    outputBinding:
      glob: "*.processed.txt"

arguments:
  - valueFrom: |
      input_file=$1
      output_file=$(basename $input_file .txt).processed.txt
      head -n -1 $input_file > $output_file
    shellQuote: false
