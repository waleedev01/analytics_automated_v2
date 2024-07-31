cwlVersion: v1.2
class: Workflow

inputs:
  input_file:
    type: File
    inputBinding:
      position: 1

outputs:
  output_file:
    type: File
    outputBinding:
      glob: output.txt

steps:
  step1:
    run: CommandLineTool.cwl
    in:
      input_file: input_file
    out:
      output_file: output.txt

  step2:
    run: command_line_tool_2.cwl
    in:
      input_file: step1/output_file
    out:
      output_file: output.txt

requirements:
  - class: CommandLineTool
    requirements:
      - class: InlineJavascriptRequirement
      - class: InitialWorkDirRequirement
        listing:
          - entry: $(inputs.input_file.path)
            entryname: input.txt

  - class: CommandLineTool
    requirements:
      - class: DockerRequirement
        dockerPull: ubuntu:latest