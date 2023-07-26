import pytesseract
from pdf2image import convert_from_path
from django.shortcuts import render, redirect
from .models import MedicalRecord
from .forms import DocumentUploadForm
import tempfile
from .process import extract_info_with_gpt3
from celery.result import AsyncResult

def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save file
            document = form.cleaned_data.get('document')

            # Save InMemoryUploadedFile to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as fp:
                for chunk in document.chunks():
                    fp.write(chunk)
                temp_file_path = fp.name

            # Convert PDF to images
            images = convert_from_path(temp_file_path)

            # Pick the first image (first page)
            image = images[0]

            # Perform OCR on the first image
            text = pytesseract.image_to_string(image)

            # Use GPT-3 to extract name, birthdate, and age
            task = extract_info_with_gpt3.delay(text)

            # Create a new MedicalRecord
            record = MedicalRecord(name='Pending', text=text, task_id=task.id)
            record.save()

            # Wait for the task to finish and get the result
            task.wait()

            # Update the MedicalRecord with the extracted information
            name, birthdate, age = task.result
            record.name = name
            record.birthdate = birthdate
            record.age = age
            record.save()

            return redirect('upload_document')
    else:
        form = DocumentUploadForm()

    return render(request, 'upload.html', {'form': form})
