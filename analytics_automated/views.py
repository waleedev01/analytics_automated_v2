from django.shortcuts import render
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .cwl_parser import read_cwl_file, CWLSchemaValidator
import logging
import yaml

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
        for file in files:
            if not file.name.endswith('.cwl'):
                logging.error(f"Uploaded file is not a CWL file: {file.name}")
                return render(request, 'cwl/upload_cwl.html', {"message": f"Uploaded file is not a CWL file: {file.name}"})
            
            path = default_storage.save('cwl_workflows/' + file.name, ContentFile(file.read()))
            full_path = default_storage.path(path)
            file_paths[file.name] = full_path
        
        # Parse each CWL file
        try:
            workflow_files = {}
            for file_name, full_path in file_paths.items():
                with open(full_path, 'r') as cwl_file:
                    cwl_data = yaml.safe_load(cwl_file)
                cwl_class = cwl_data.get("class")

                if cwl_class == "Workflow":
                    workflow_files[file_name] = cwl_data

            for workflow_name, workflow_data in workflow_files.items():
                read_cwl_file(file_paths[workflow_name], file_paths)
            
            logging.info(f"Successfully processed CWL files: {', '.join(file_paths.keys())}")
            return render(request, 'cwl/upload_cwl.html', {"message": "CWL files processed successfully", "file_names": list(file_paths.keys())})
        except Exception as e:
            logging.error(f"Failed to process CWL files: {str(e)}")
            return render(request, 'cwl/upload_cwl.html', {"message": str(e)})
