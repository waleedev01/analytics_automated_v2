# This is a manually created example file for the task in AAv1 called memembed

class: Workflow
cwlVersion: v1.2

inputs:
  input_file: File

outputs:
  output_pdb:
    type: File
    outputSource: memembed2/output_pdb

steps:
  memembed2:
    run:
      class: CommandLineTool

      baseCommand: /home/dbuchan/Code/bin/memembed

      stdout: "$(inputs.input_file.basename).stdout"

      inputs:
        memembed_algorithm:
            type: string
            default: "0"
            inputBinding:
                position: 1
                prefix: -s
        memembed_barrel:
            type: boolean
            default: true
            inputBinding:
                position: 2
                prefix: -b
        memembed_termini:
            type: string
            default: "in"
            inputBinding:
                position: 3
                prefix: -n
        input_file:
            type: File
            inputBinding:
                position: 4

      outputs:
        output_pdb:
            type: File
            outputBinding:
                glob: "*.pdb"
        
    in:
      input_file: input_file
    out: 
      - output_pdb
