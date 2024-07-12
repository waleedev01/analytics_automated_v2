This is an example of an invalid CWL file with missing required fields:

```
cwlVersion: v1.0
class: CommandLineTool

inputs:
  input_file:
    type: File

outputs:
  output_file:
    type: File

baseCommand: cat
```