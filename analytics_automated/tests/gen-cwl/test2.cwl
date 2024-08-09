cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo

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
      prefix: "--input-file"

outputs:
  output_file:
    type: stdout

stdout: /home/gty/vv-project/celery-requirement/analytics_automated_v2/analytics_automated/output/output.txt

