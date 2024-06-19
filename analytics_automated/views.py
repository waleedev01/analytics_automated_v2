from django.shortcuts import render
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .cwl_parser import read_cwl_file
import logging
import os

logger = logging.getLogger(__name__)


class CWLUploadPageView(View):
    def get(self, request):
        return render(request, 'cwl/upload_cwl.html')
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            logging.error("No file provided in upload.")
            return render(request, 'cwl/upload_cwl.html', {"message": "No file provided"})
        
        if not file.name.endswith('.cwl'):
            logging.error("Uploaded file is not a CWL file.")
            return render(request, 'cwl/upload_cwl.html', {"message": "Uploaded file is not a CWL file"})
        
        # Save the file to a temporary location and get the full path
        path = default_storage.save('analytics_automated/cwl_files/' + file.name, ContentFile(file.read()))
        full_path = default_storage.path(path)
        
        # Parse the CWL file
        try:
            task_id = read_cwl_file(full_path)
            logging.info(f"Successfully processed CWL file: {full_path}")
            return render(request, 'cwl/upload_cwl.html', {"message": "CWL file processed successfully", "task_id": task_id})
        except Exception as e:
            logging.error(f"Failed to process CWL file: {str(e)}")
            return render(request, 'cwl/upload_cwl.html', {"message": str(e)})
