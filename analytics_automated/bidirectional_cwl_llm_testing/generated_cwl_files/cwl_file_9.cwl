cwlVersion: v1.0
class: CommandLineTool
inputs: 
  input_file:
    type: File
baseCommand: echo "Hello World"

outputs: 
  - id: output_file
    type: Directory