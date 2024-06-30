from django.shortcuts import render
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .cwl_utils.cwl_parser import read_cwl_file
from .cwl_utils.cwl_schema_validator import CWLSchemaValidator
import logging
import yaml
import os

logger = logging.getLogger(__name__)

class CWLUploadPageView(View):
    def get(self, request):
        return render(request, 'cwl/upload_cwl.html')
    
    def post(self, request):
        files = request.FILES.getlist('files')
        if not files:
            logging.error("No files provided in upload.")
            return render(request, 'cwl/upload_cwl.html', {"message": "No files provided"})
        
        file_paths = {}
        messages = []
        for file in files:
            if not file.name.endswith('.cwl'):
                logging.error(f"Uploaded file is not a CWL file: {file.name}")
                messages.append(f"Uploaded file is not a CWL file: {file.name}")
                continue
            
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
            
            # Clean up uploaded files
            for file_name, full_path in file_paths.items():
                os.remove(full_path)

            logging.info(f"Successfully processed CWL files: {', '.join(file_paths.keys())}")
            return render(request, 'cwl/upload_cwl.html', {"message": "Results Below:", "file_names": list(file_paths.keys()), "messages": messages})
        except Exception as e:
            logging.error(f"Failed to process CWL files: {str(e)}")
            return render(request, 'cwl/upload_cwl.html', {"message": str(e), "messages": messages})
