import pytesseract
from pdf2image import convert_from_path
from django.shortcuts import render, redirect
from .models import MedicalRecord
from .forms import DocumentUploadForm
import tempfile
from .process import extract_info_with_gpt3

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

            # Iterate through images and perform OCR
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)

                # Use GPT-3 to extract name, birthdate, and age
                name, birthdate, age = extract_info_with_gpt3(text)

                # Create a new MedicalRecord
                record = MedicalRecord(name=name, birthdate=birthdate, age=age, text=text)
                record.save()

            return redirect('upload_document')
    else:
        form = DocumentUploadForm()

    return render(request, 'upload.html', {'form': form})
