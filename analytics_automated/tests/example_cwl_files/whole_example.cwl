cwlVersion: v1.2
class: Workflow

requirements:
  ScatterFeatureRequirement: {}

inputs: {}

outputs:
  merged_file:
    type: File
    outputSource: merge_files/merged_output

steps:
  generate_files:
    run:
      class: CommandLineTool
      baseCommand: bash
      arguments:
        - -c
        - |
          for i in {1..3}; do
            filename="file$i.txt"
            for j in {1..5}; do
              echo $RANDOM >> $filename
            done
          done
      inputs: []
      outputs:
        output_files:
          type: File[]
          outputBinding:
            glob: "*.txt"
    in: {}
    out: [output_files]

  process_files:
    run:
      class: CommandLineTool
      baseCommand: bash
      inputs:
        input_file:
          type: File
          inputBinding:
            position: 1
      outputs:
        processed_files:
          type: File
          outputBinding:
            glob: "*.processed.txt"
      arguments:
        - valueFrom: |
            input_file=$1
            output_file=$(basename $input_file .txt).processed.txt
            head -n -1 $input_file > $output_file
          shellQuote: false
    in:
      input_file: generate_files/output_files
    out: [processed_files]
    scatter: input_file

  merge_files:
    run:
      class: CommandLineTool
      baseCommand: bash
      inputs:
        input_files:
          type: File[]
          inputBinding:
            prefix: "--files"
            itemSeparator: " "
      outputs:
        merged_output:
          type: File
          outputBinding:
            glob: merged_output.txt
      arguments:
        - valueFrom: |
            output_file="merged_output.txt"
            cat $@ > $output_file
          shellQuote: false
    in:
      input_files: process_files/processed_files
    out: [merged_output]
