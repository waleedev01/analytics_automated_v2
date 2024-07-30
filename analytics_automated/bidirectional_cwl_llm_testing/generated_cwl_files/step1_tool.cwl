cwlVersion: v1.0
class: CommandLineTool
baseCommand: step1_script.sh

inputs:
  input_files:
    type:
      - File
    inputBinding:
      position: 1
      prefix: --input-files

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output_file.txt