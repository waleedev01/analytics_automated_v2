import logging
import os
import shutil
import yaml
import zipfile
import tempfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from .cwl_utils.cwl_parser import read_cwl_file
from .cwl_utils.cwl_schema_validator import CWLSchemaValidator
from .cwl_utils.reconstruct_cwl import reconstruct_cwl_files
from .models import Job
from .workflow_visualization import *

logger = logging.getLogger(__name__)

def DownloadCWLView(request):
    """
    Handles the download of CWL files associated with a specific job.

    This view processes POST requests to download CWL files for a given job as a zip archive. 
    It reconstructs the CWL files using the job name, compresses them into a zip file, 
    and returns it as an HTTP response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A response with the CWL files in a zip archive or a rendered error page.
    """
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        if not job_name:
            logger.error("No job name provided in request.")
            return render(request, 'admin/download_cwl.html', {
                "messages": ["No job name provided"],
                "jobs": Job.objects.all()
            })

        try:
            job = Job.objects.get(name=job_name)
        except Job.DoesNotExist:
            logger.error(f"Job '{job_name}' does not exist.")
            return render(request, 'admin/download_cwl.html', {
                "messages": [f"Job '{job_name}' does not exist"],
                "jobs": Job.objects.all()
            })

        # Create temporary directory for CWL files
        with tempfile.TemporaryDirectory() as temp_dir:
            reconstruct_cwl_files(job_name, temp_dir)
            zip_file_path = os.path.join(temp_dir, f"{job_name}_cwl.zip")
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)

            with open(zip_file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={job_name}_cwl.zip'
                return response

    return render(request, 'admin/download_cwl.html', {"jobs": Job.objects.all()})

def UploadCWLView(request):
    """
    Handles the upload and processing of CWL files.

    This view processes POST requests for uploading CWL files. It saves the uploaded files, 
    parses them to differentiate between Workflow and CommandLineTool classes, 
    and processes the workflows accordingly. After processing, the uploaded files are removed.

    Args:
        request (HttpRequest): The HTTP request object with uploaded files.

    Returns:
        JsonResponse: A JSON response with the results of the file processing or error messages.
    """
    if request.method == 'POST':
        logger.info("Handling file upload.")
        files = request.FILES.getlist('files')
        if not files:
            logger.error("No files provided in upload.")
            return JsonResponse({"messages": ["No files provided"]})

        file_paths = {}
        messages = []
        for file in files:
            if not file.name.endswith('.cwl'):
                logger.error(f"Uploaded file is not a CWL file: {file.name}")
                messages.append(f"Uploaded file is not a CWL file: {file.name}")
                continue

            # Save the uploaded file to the storage
            path = default_storage.save('cwl_workflows/' + file.name, ContentFile(file.read()))
            full_path = default_storage.path(path)
            file_paths[file.name] = full_path

        # Parse each CWL file
        try:
            workflow_files_temp = {}
            workflow_files = {}
            for file_name, full_path in file_paths.items():
                with open(full_path, 'r') as cwl_file:
                    cwl_data = yaml.safe_load(cwl_file)
                cwl_class = cwl_data.get("class")

                if cwl_class == "Workflow":
                    workflow_files_temp[file_name] = cwl_data
                elif cwl_class == "CommandLineTool":
                    workflow_files[file_name] = cwl_data

            # Put workflow file at the end of the list
            for file_name, cwl_data in workflow_files_temp.items():
                workflow_files[file_name] = cwl_data

            if not workflow_files:
                messages.append("No workflow files found in the uploaded files.")
            else:
                for workflow_name in workflow_files:
                    filename = workflow_name.split('.')[0]
                    read_cwl_file(file_paths[workflow_name], filename, messages)

            # Clean up uploaded files after processing
            for file_name, full_path in file_paths.items():
                os.remove(full_path)

            logger.info(f"Successfully processed CWL files: {', '.join(file_paths.keys())}")
            return JsonResponse({"file_names": list(file_paths.keys()), "messages": messages})
        except Exception as e:
            logger.error(f"Failed to process CWL files: {e}")
            return JsonResponse({"messages": [str(e)]})

    return render(request, 'admin/upload_cwl.html')

class StaticWorkflowGraphView(View):
    """
    Generate and display a static workflow graph for a specific job.

    This view generates a static workflow visualization based on tasks associated with a specific job. 
    It renders the generated graph as an image in a web page.

    Args:
        request (HttpRequest): The HTTP request object.
        job_name (str): The name of the job for which to generate the workflow graph.

    Returns:
        HttpResponse: A rendered web page with the static workflow graph or an error message.
    """
    def get(self, request, job_name=None):
        try:
            # Find the job with the given job_name
            job = Job.objects.get(name=job_name)
            
            # Get tasks related to this job via the Step model
            steps = Step.objects.filter(job=job)
            tasks = Task.objects.filter(id__in=steps.values_list('task_id', flat=True))

            if not tasks:
                logger.error(f'No tasks available for visualization for job: {job_name}.')
                return render(request, 'workflow_visualization.html', {'error': f'No tasks available for visualization for job: {job_name}.'})

            img_data = plot_static_workflow2(tasks)
            logger.info(f'Static workflow graph successfully generated for job: {job_name}.')
            return render(request, 'workflow_visualization.html', {'img_data': img_data, 'job_name': job_name})
        except Job.DoesNotExist:
            logger.error(f'Job not found: {job_name}')
            return render(request, 'workflow_visualization.html', {'error': f'Job not found: {job_name}'})
        except Exception as e:
            logger.error(f'Error generating static workflow graph for job {job_name}: {e}')
            return render(request, 'workflow_visualization.html', {'error': 'An error occurred while generating the visualization.'})


class DashboardView(View):
    """
    Display a dashboard with task states for a specific submission.

    This view provides an overview of the current states of tasks associated with a particular submission. 
    It renders a dashboard showing task details and their states.

    Args:
        request (HttpRequest): The HTTP request object.
        submission_name (str): The name of the submission for which to display the task states.

    Returns:
        HttpResponse: A rendered web page with the dashboard or an error message.
    """
    def get(self, request, submission_name):
        logger.info('Fetching data for dashboard.')

        # Fetch task states for a specific submission, e.g., the first one
        task_states = {}
        
        try:
            task_states = get_current_task_states2(submission_name)
        except Submission.DoesNotExist:
            task_states = {'error': 'Submission not found'}
        except Exception as e:
            task_states = {'error': 'An error occurred while retrieving task states'}

        context = {
            'task_states': task_states,
            'submission_name': submission_name,
        }

        logger.info('Dashboard data successfully retrieved.')
        return render(request, 'dashboard.html', context)


class TaskStatesView(View):
    """
    Retrieve and display task states for a specific submission.

    This view retrieves the states of tasks related to a given submission and renders them on a dashboard.

    Args:
        request (HttpRequest): The HTTP request object.
        submission_name (str): The name of the submission for which to retrieve task states.

    Returns:
        HttpResponse: A rendered web page with the task states or an error message.
    """
    def get(self, request, submission_name):
        logger.info(f'Retrieving task states for submission: {submission_name}')
        try:
            task_states = get_current_task_states2(submission_name)
            logger.info('Task states successfully retrieved.')
            return render(request, 'dashboard.html', {'task_states': task_states, 'submission_name': submission_name})
        except Submission.DoesNotExist:
            logger.error(f'Submission not found: {submission_name}')
            return render(request, 'dashboard.html', {'error': 'Submission not found', 'submission_name': submission_name})
        except Exception as e:
            logger.error(f'Error retrieving task states for submission {submission_name}: {e}')
            return render(request, 'dashboard.html', {'error': 'An error occurred while retrieving task states', 'submission_name': submission_name})
    
