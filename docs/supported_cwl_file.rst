
CWL File Requirements and Specifications
========================================

The AAv2 platform allows users to upload specific CWL files. Besides all the required fields specified in the Common Workflow Language Standards, AAv2 covers a subset of them with additional constraints and requirements to ensure proper functionality within the system.

Supported CWL Version
---------------------

- `1.2 <https://www.commonwl.org/v1.2/>`_

Supported CWL Classes
---------------------

1. `Workflow <https://www.commonwl.org/v1.2/Workflow.html#Workflow>`_
2. `CommandLineTool <https://www.commonwl.org/v1.2/CommandLineTool.html#CommandLineTool>`_

Supported CWL Requirement List
------------------------------

- **ShellCommandRequirement**: Enables the use of shell commands within the CWL tool.
- **EnvVarRequirement**: Allows the specification of environment variables.
- **InitialWorkDirRequirement**: Specifies files that must be staged into the initial working directory.
- **InlineJavascriptRequirement**: **Only** for `conditional workflows <#conditional-workflow-type>`_, allows the use of inline JavaScript expressions.

Supported Hint Field
--------------------

- **SoftwareRequirement**: Specifies software packages that are required.

Special Requirements
--------------------

1. Requirements must be defined as a list/array:

   - Even if there is only one requirement, it must be defined as a list.

   - Example:

     .. code-block:: yaml

        requirements:
          - class: ShellCommandRequirement

2. Inputs of CommandLineTool must be defined as a `dictionary/map <https://www.commonwl.org/v1.2/CommandLineTool.html#map>`_:

   - Inputs should be specified using a dictionary format.

   - Example:

     .. code-block:: yaml

        inputs:
          input_file:
            type: File
            inputBinding:
              position: 1

3. baseCommand **cannot** be empty.

   - **baseCommand**: The command to be executed.

   - Example:

     .. code-block:: yaml

        baseCommand: echo

Conditional Workflow Type
-------------------------

AAv2 supports conditional workflows using the `InlineJavascriptRequirement`. This feature allows the workflow

to execute steps based on certain conditions, and the conditional execution is defined using the `when` field in a workflow step.

Key Points for Conditional Workflows:
-------------------------------------

- **InlineJavascriptRequirement**: This requirement must be specified to enable conditional execution.
- **`when` Field Format**: The `when` field must follow the format `$(inputs.<input_name> <condition>)`. Currently, the supported condition is based on the `exit_code` of previous steps.
- **CWL Version Compatibility**: The `when` field is supported in CWL version 1.2 and above.

Simple CWL Guidance
===================

For users who are not familiar with CWL and want a quick overview, this section provides a simple and straightforward guide to creating CWL files compatible with the AAv2 platform. The following examples and explanations will help you understand the basic structure and required attributes of CWL files, making it easier to get started.

General Structure
-----------------

- **cwlVersion**: Indicates the version of the CWL used.

  - Example:

    .. code-block:: yaml

       cwlVersion: v1.2

- **class**: Specifies whether the document is a Workflow or CommandLineTool.

  - Example:

    .. code-block:: yaml

       class: CommandLineTool

CommandLineTool Attributes
--------------------------

- **baseCommand**: The command to be executed.

  - Example:

    .. code-block:: yaml

       baseCommand: echo

- **inputs**: Defined as a dictionary, each input must specify the type and may include inputBinding.

  - Example:

    .. code-block:: yaml

       inputs:
         message:
           type: string
           inputBinding:
             position: 1

- **outputs**: Outputs should also be defined using a dictionary.

  - Example:

    .. code-block:: yaml

       outputs:
         output_file:
           type: File
           outputBinding:
             glob: output.txt

- **requirements**: Must be a list of supported requirements.

  - Example:

    .. code-block:: yaml

       requirements:
         - class: ShellCommandRequirement
         - class: EnvVarRequirement
           envDef:
             - envName: HOME
               envValue: /home/user

- **hints**: Specifically for SoftwareRequirement, defined as a list.

  - Example:

    .. code-block:: yaml

       hints:
         - class: SoftwareRequirement
           packages:
             - package: python
               version: [2.7, 3.5+]

- **arguments**: Additional command-line arguments (optional).

  - Example:

    .. code-block:: yaml

       arguments: ["--verbose"]

- **stdin, stdout, stderr**: Standard input, output, and error specifications (optional).

  - Example:

    .. code-block:: yaml

       stdout: output.txt

Workflow Attributes
-------------------

- **steps**: Define the steps in the workflow, each step may run a CommandLineTool or another Workflow.

  - Example:

    .. code-block:: yaml

       steps:
         step1:
           run: tool.cwl
           in:
             message: input_message
           out: [output_file]

- **requirements**: Similar to CommandLineTool, must be defined as a list.

  - Example:

    .. code-block:: yaml

       requirements:
         - class: InlineJavascriptRequirement

- **inputs**: Workflow inputs defined as a dictionary.

  - Example:

    .. code-block:: yaml

       inputs:
         input_message:
           type: string

- **outputs**: Workflow outputs defined as a dictionary.

  - Example:

    .. code-block:: yaml

       outputs:
         result:
           type: File
           outputSource: step1/output_file
