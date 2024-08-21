cwlVersion: v1.2
class: CommandLineTool
baseCommand: printenv
inputs:
  var_name:
    type: string
    inputBinding:
      position: 1
outputs:
  var_value:
    type: stdout
