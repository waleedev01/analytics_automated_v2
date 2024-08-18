# This is a manually created example file for the task in AAv1 called epestfind
# example: 1 input, 1 output
class: CommandLineTool
cwlVersion: v1.2
baseCommand:
  - /home/dbuchan/Applications/EMBOSS-6.4.0/emboss/epestfind
arguments:
  - prefix: -graph
    valueFrom: "NO"
    position: 1
    separate: True
  - prefix: -window
    valueFrom: "10"
    position: 2
    separate: False
  - prefix: -order
    valueFrom: "2"
    position: 3
  - prefix: -threshold
    valueFrom: "5.0"

inputs:
  input_file:
    type: File
    inputBinding:
      format: ".sing"
outputs:
  output_file:
    type: File
    outputBinding:
      glob: "*.pest"

stdout: "*.stdout"