cwlVersion: v1.0

invalidWorkflow:
  class: Workflow

  steps:
    step1:
      run: tool.cwl
      in:
        input_file: file
      out:
        output_file: file

  outputs:
    final_output:
      type: File
      outputSource: step1.output_file