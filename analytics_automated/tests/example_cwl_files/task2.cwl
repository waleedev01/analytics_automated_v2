cwlVersion: v1.0
class: CommandLineTool
baseCommand: cat
inputs:
  input1:
    type: File
    inputBinding:
      position: 1
outputs:
  output1:
    type: stdout
stdout: output.txt
arguments: ["--verbose"]
stdin: $(inputs.input1.path)
successCodes: [0]
temporaryFailCodes: [1]
permanentFailCodes: [2]
