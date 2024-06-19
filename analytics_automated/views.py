from django.shortcuts import render
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
#from .cwl_parser import read_cwl_file change this

class CWLUploadPageView(View):
    def get(self, request):
        return render(request, 'cwl/upload_cwl.html')
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return render(request, 'cwl/upload_cwl.html', {"message": "No file provided"})
        
        # Save the file to a temporary location
        path = default_storage.save('tmp/' + file.name, ContentFile(file.read()))
        
        # Parse the CWL file
        try:
            task_id = read_cwl_file(path)
            return render(request, 'cwl/upload_cwl.html', {"message": "CWL file processed successfully", "task_id": task_id})
        except Exception as e:
            return render(request, 'cwl/upload_cwl.html', {"message": str(e)})
