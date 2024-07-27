cwlVersion: v1.2
class: Workflow

inputs:
  message: 
    type: File

outputs:
  result:
    type: string
    outputSource: step2/out

steps:
  step1:
    run:
      class: CommandLineTool
      baseCommand: cat
      stdout: output.txt
      
      inputs:
        message1:
          type: File
          inputBinding: {}
      outputs:
        out:
          type: int
          outputBinding:
            outputEval: $(runtime.exitCode)
        file:
          type: File
          outputBinding:
            glob: "*.txt"
    in:
      message1: message
    out: [out, file]

  step2:
    run:
      class: CommandLineTool
      baseCommand: cat
      stdout: output.txt
      
      inputs:
        message2:
          type: File
          format: ".txt"
          inputBinding: {}
        exit_code:
          type: int
      outputs:
        out:
          type: File
          outputBinding:
            glob: "*.txt"
    in:
      message2: step1/file
      exit_code: step1/out
    out: [out]
    when: $(inputs.exit_code == 128)

requirements:
  - InlineJavascriptRequirement: {}
