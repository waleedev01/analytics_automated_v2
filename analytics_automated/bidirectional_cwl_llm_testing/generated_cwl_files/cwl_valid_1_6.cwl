cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  message:
    type: Any
    inputBinding:
      position: 1
outputs:
  output_message:
    type: Any

cwlVersion: v1.1
class: CommandLineTool
baseCommand: ls
inputs:
  directory:
    type: Any
    inputBinding:
      position: 1
outputs:
  output_list:
    type: Any

cwlVersion: v1.2
class: CommandLineTool
baseCommand: touch
inputs:
  file:
    type: Any
    inputBinding:
      position: 1
outputs:
  output_file:
    type: Any