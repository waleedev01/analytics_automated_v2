cwlVersion: v1.2
class: Workflow

# Define the first CommandLineTool step
steps:
  step1:
    run: tool1.cwl  # Reference the CommandLineTool file for step1
    in:
      input1: step1_input1  # Define input for step1
    out:
      output1: step1_output1  # Define output for step1

  # Define the second CommandLineTool step
  step2:
    run: tool2.cwl  # Reference the CommandLineTool file for step2
    in:
      input2: step2_input2  # Define input for step2
    out:
      output2: step2_output2  # Define output for step2

# Define the inputs for the workflow
inputs:
  workflow_input1: string  # Define input for the workflow

# Define the outputs for the workflow
outputs:
  workflow_output1: string  # Define output for the workflow