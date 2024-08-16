cwlVersion: v1.2
class: CommandLineTool
baseCommand: [sh, -c]
arguments:
  - |
    cat $(inputs.file1.path) $(inputs.file2.path) > concatenated.txt
inputs:
  file1:
    type: File
    inputBinding:
      position: 1
  file2:
    type: File
    inputBinding:
      position: 2
outputs:
  output_file:
    type: File
    outputBinding:
      glob: "concatenated.txt"  
