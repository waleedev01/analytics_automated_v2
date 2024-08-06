cwlVersion: v1.2
class: CommandLineTool
baseCommand: /home/dbuchan/Applications/coils/coils.sh
doc: Runs coils2

inputs:
  ID:
    type: string
    default: "$ID"
    inputBinding:
      position: 1
  input_file:
    type: File
    inputBinding:
      position: 2
      valueFrom: $(runtime.tmpdir)/$(inputs.ID)/$(inputs.I1.basename)
    format: ".sing"

outputs:
  output_ss:
    type: File
    outputBinding:
      glob: "*.coils"

stdout: "*.coils"
