cwlVersion: v1.0

hints:
  DockerRequirement:
    dockerPull: ubuntu:latest

steps:
  - run: echo "Hello, world!"
    outputs:
      - id: output_file
        type: File
        outputBinding:
          glob: "output.txt"