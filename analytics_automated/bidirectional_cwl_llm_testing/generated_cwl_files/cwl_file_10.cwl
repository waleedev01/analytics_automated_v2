cwlVersion: v1.0

cwlMissingField: true

steps:
  - run: script.sh
    in:
      input_file: input.txt
    out:
      output_file: output.txt