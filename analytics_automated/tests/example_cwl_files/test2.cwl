cwlVersion: v1.0
class: CommandLineTool
baseCommand: cat

requirements:
  - class: InitialWorkDirRequirement
    listing:
      - class: File
        entryname: config.txt
        entry: |
          {
            "param1": "value1",
            "param2": "value2"
          }

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output:
    type: stdout

