cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
      prefix: "--input-file"

outputs:
  output_file:
    type: stdout

stdout: /home/gty/vv-project/analytics_automated_v2/analytics_automated/output/output.txt
