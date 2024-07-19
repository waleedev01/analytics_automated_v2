cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: string
    inputBinding:
      position: 1
outputs:  # missing 'outputs' section
requirements:
  InitialWorkDirRequirement:
    listing:
      - entryname: input_file.txt
        entry: $(inputs.message)
  ShellCommandRequirement: {}
stdout: output.txt