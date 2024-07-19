cwlVersion: v1.2
class: CommandLineTool

inputs:
  fastq_file:
    type: File
    inputBinding:
      position: 1
      prefix: --input

outputs:
  trimmed_fastq_file:
    type: File
    outputBinding:
      glob: output/*.fastq