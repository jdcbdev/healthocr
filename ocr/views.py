import pytesseract
from pdf2image import convert_from_path
from dateutil.parser import parse as parse_date
from django.shortcuts import render, redirect
from .models import MedicalRecord
from .forms import DocumentUploadForm
import tempfile

def extract_info(prefix, text):
    for line in text.split('\n'):
        if line.lower().startswith(prefix.lower()):
            return line[len(prefix) + 1:]
    return None

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

                # Extract and parse name, birthdate, and age
                name = extract_info('name:', text)
                birthdate_str = extract_info('birthdate:', text)
                if birthdate_str is not None:
                    birthdate_str = birthdate_str.strip().split(':')[-1]
                    try:
                        birthdate = parse_date(birthdate_str.strip())
                    except Exception:
                        birthdate = None
                else:
                    birthdate = None

                age_str = extract_info('age:', text)
                if age_str is not None:
                    try:
                        age = int(age_str.split(':')[-1].strip())
                    except ValueError:
                        age = None
                else:
                    age = None

                # Create a new MedicalRecord
                record = MedicalRecord(name=name, birthdate=birthdate, age=age, text=text)
                record.save()

            return redirect('upload_document')
    else:
        form = DocumentUploadForm()

    return render(request, 'upload.html', {'form': form})
