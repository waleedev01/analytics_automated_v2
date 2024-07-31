cwlVersion: v1.2
class: CommandLineTool
baseCommand: echo
inputs:
  input_file:
    type: File
    inputBinding:
      position: 1
outputs:
  output_file:
    type: stdout

This CWL file defines a CommandLineTool with a baseCommand of "echo" that takes a input_file of type File as input and outputs the result to stdout.