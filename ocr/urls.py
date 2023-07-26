from django.urls import path
from . import views  # Import your views here.

urlpatterns = [
    path('', views.upload_document, name='upload_document'),
    # Add other paths for your 'ocr' app here as needed.
]
