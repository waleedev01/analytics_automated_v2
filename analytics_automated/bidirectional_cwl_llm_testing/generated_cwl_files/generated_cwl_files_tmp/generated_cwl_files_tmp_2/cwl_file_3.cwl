cwlVersion: v1.0
class: CommandLineTool
inputs:
  input_file:
    type: File
    label: Input file
outputs:
  output_file:
    type: File
    label: Output file
baseCommand: cat
stdout: output.txt
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.input_file)
        entryName: input.txt
        writable: false
stdout: output.txt