cwl:
  class: CommandLineTool
  inputs:
    input_file:
      type: File
      inputBinding: 
        position: 1
  outputs: 
    output_file: 
      type: File
  baseCommand: ls
  arguments: ['-lh']