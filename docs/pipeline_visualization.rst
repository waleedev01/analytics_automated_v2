.. _using_pipeline_visualization:

Using Pipeline Visualization
==================

Pipeline visualization is a powerful feature that allows users to monitor and visualize the execution of workflows defined using the Common Workflow Language (CWL). This guide provides instructions on how to use the pipeline visualization features.

Static Visualization
^^^^^^^^^^^^^^^^

Viewing Static Workflow:
Visit http://127.0.0.1:8000/static-visualize/ to access a static representation of your CWL-defined workflow.
This visualization shows the predefined structure, task dependencies, and the sequence of tasks as they are intended to be executed.
The static graph includes task names, descriptions, and dependencies, providing a clear overview of the workflow.


Dynamic Visualization
^^^^^^^^^^^^^^^^

Monitoring Workflow Execution:
Before you can monitor your workflow dynamically, you must create a submission. To do this, submit your CWL file to the system.
Once the submission is created, visit http://127.0.0.1:8000/dynamic-visualize/<submission_name> (Replace <submission_name> with the actual name of your submission) to monitor the execution of your workflow in real-time.
The dynamic visualization updates automatically to reflect the current state of each task (e.g., running, completed, pending, failed).
Tasks are color-coded based on their state to provide immediate visual feedback on the workflow's progress.
Real-Time Updates: The dynamic visualization refreshes periodically to show the latest status of each task.


Submitting Workflows:
To visualize a workflow, users must first submit their CWL file. You can submit a CWL workflow by navigating to http://127.0.0.1:8000/admin_upload_cwl/ and uploading the CWL file.
The system parses the file, creates a submission, and prepares it for both static and dynamic visualization.


POST Requests
^^^^^^^^^^^^^^^^

Submitting Workflow Data:
Submit the CWL workflow data using a POST request to the appropriate URI. This submission triggers the visualization process.
Successful submissions will return a JSON response, including a submission_name, which can be used to track the visualization.
Input Requirements: The CWL file must be valid and conform to the expected schema. The system validates the file upon submission.


Checking Task States
^^^^^^^^^^^^^^^^

Polling Visualization Data:
Users can poll for updates on the visualization by sending a GET request to http://127.0.0.1:8000/api/task-states/<submission_name>
Replace <submission_name> with the actual name of your submission.
The response will include the current states of all tasks in the workflow, which will be reflected in the dynamic visualization.
Example: A successful response will include data indicating whether tasks are running, completed, pending, or failed, along with any output data generated.

Advanced Visualization Features
^^^^^^^^^^^^^^^^

Graph Customization:
The system allows for advanced customization of the visualizations, including adjusting node sizes based on the number of dependencies, displaying task descriptions, and adding hover details for better clarity.
Users can adjust visualization settings via the UI or by modifying the underlying visualization scripts.
Color-Coding and Labels: Task nodes are color-coded, and labels can include additional details like the number of dependencies, task inputs, outputs, and current status.


Error Handling
^^^^^^^^^^^^^^^^

Handling Visualization Errors:
The system provides clear error messages if there are issues with the CWL file or the visualization process.
Errors are displayed directly in the visualization interface, allowing users to quickly diagnose and resolve issues.
