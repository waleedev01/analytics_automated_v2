cwlVersion: v1.0

workflows:
  missing_fields_workflow:
    steps:
      step1:
        run: shell_script.cwl
        in:
          input_value: input.txt
        out:
          - output_value: output.txt