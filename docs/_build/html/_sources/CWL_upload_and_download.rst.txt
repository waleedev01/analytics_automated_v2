.. _CWL_upload_and_download:

CWL Upload and Download
=======================

The CWL Upload Page allows users to upload multiple CWL files.
The system processes these files in the background and creates
new :ref:`tasks or jobs <the_Job_UI>` based on the CWL file types.
The CWL Download Page enables users to select existing jobs
in the system and generate multiple executable CWL files.

Create Job Via CWL Example
--------------------------

In this example, the user will create two Tasks, ``create_file`` and ``write_message``, and a Job named ``createHelloWorld``.

-  ``create_file.cwl``

.. code:: yaml

   Copy codecwlVersion: v1.2

   class: CommandLineTool

   baseCommand: [touch]

   inputs:

     filename:

       type: string

       inputBinding:

         position: 1

       default: "test.txt"

   outputs:

     created_file:

       type: File

       outputBinding:

         glob: "*.txt"

-  ``write_message.cwl``

.. code:: yaml

   cwlVersion: v1.2

   class: CommandLineTool

   baseCommand: [bash, -c]

   inputs:

     filename:

       type: File

       inputBinding:

         position: 2

     message:

       type: string

       inputBinding:

         position: 1

         prefix: "echo"

       default: "Hello World"

   outputs:

     output_file:

       type: File

       outputBinding:

         glob: "*.txt"

- ``createHelloWorld.cwl``

.. code:: yaml

   cwlVersion: v1.2

   class: Workflow

   inputs:

     message:

       type: string

       default: "Hello World."

   outputs:

     final_output:

       type: File

       outputSource: write_message/output_file

   steps:

     create_file:

       run: create_file.cwl

       in:

         filename:

           default: "test.txt"

       out: [created_file]

     write_message:

       run: write_message.cwl

       in:

         filename: create_file/created_file

         message: message

       out: [output_file]

Step to Upload CWL Files
^^^^^^^^^^^^^^^^^^^^^^^^

1. Before uploading any CWL files, please ensure that there is at least one available :ref:`Backend <define_backend>` in the system.

2. Access the CWL Upload Page: Navigate to

    http://127.0.0.1:8000/admin/analytics_automated/uploadcwlmodel/

3. Upload CWL Files:

   -  Click the "Choose files" button.

   -  Select the three CWL files (``create_file.cwl``, ``write_message.cwl``, ``createHelloWorld.cwl``).

   -  Click "Upload CWL". The order of the files does not matter; the system will automatically place the Workflow file last for parsing. If uploading files individually, ensure that Task files are uploaded before the Workflow file.

.. image:: upload_example_2.png
   :scale: 50%
   :align: center

If the files meet the `our CWL specification <supported_cwl_feature>`__, the system will successfully create two Tasks and one Job that includes these Tasks.
The tasks ``create_file`` and ``write_message`` will be created along with the ``createHelloWorld`` job that orchestrates these tasks.

.. image:: upload_example_2.5.png

Downloading Existing Data Analysis Tasks as CWL Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When users want to download existing data analysis tasks from the database as CWL files, follow these steps:

1. Access the CWL Download Page: Navigate to

   http://127.0.0.1:8000/admin/analytics_automated/downloadcwlmodel/

2. Select a Job:

   -  Click the ``Select a job`` dropdown menu.

   -  A list will appear, showing all executable jobs available in the system.

3. Download the CWL File:

   -  Select the desired job from the list.

   -  Click the ``Download CWL`` button to generate and download the CWL file.

.. image:: download_example_1.png

**Note**: Even if the tasks were initially created by uploading CWL files, the system does not guarantee that the downloaded CWL file will be identical to the originally uploaded file. The CWL file generated for download is independently created by the system.
