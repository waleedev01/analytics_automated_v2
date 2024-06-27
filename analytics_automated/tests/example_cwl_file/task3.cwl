cwlVersion: v1.0
class: CommandLineTool
baseCommand: process_files
inputs:
  files:
    type: File[]
    inputBinding:
      position: 1
  mode:
    type: string
    inputBinding:
      position: 2
outputs:
  result:
    type: stdout
stdout: results.txt
requirements:
  - class: ShellCommandRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: "tempfile.txt"
        entry: $(inputs.files[0].path)
successCodes: [0]
temporaryFailCodes: [1]
permanentFailCodes: [2]
