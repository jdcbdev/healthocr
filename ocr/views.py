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

            # Perform OCR on all images, save texts in a list
            all_texts = [pytesseract.image_to_string(image) for image in images]

            # Join all texts into a single string
            full_text = "\n".join(all_texts)

            # Create a new MedicalRecord with the full text
            record = MedicalRecord(name='Pending', text=full_text)
            record.save()

            # Use GPT-3 to extract name, birthdate, and age from the first page's text
            task = extract_info_with_gpt3.apply_async(args=[all_texts[0], record.id])

            # Update the record with the task_id
            record.task_id = task.id
            record.save()

            return redirect('upload_document')
    else:
        form = DocumentUploadForm()

    return render(request, 'upload.html', {'form': form})
