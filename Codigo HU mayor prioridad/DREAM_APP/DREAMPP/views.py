from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from PIL import Image
import numpy as np
import pydicom
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('archivo_dicom'):
        archivo_dicom = request.FILES['archivo_dicom']
        fs = FileSystemStorage()

        filename = fs.save(archivo_dicom.name, archivo_dicom)
        file_absolute_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            dicom_file = pydicom.dcmread(file_absolute_path)
            image_array = dicom_file.pixel_array.astype(float)

            rescaled_image = (np.maximum(image_array, 0) / image_array.max()) * 255
            final_image = np.uint8(rescaled_image)

            final_image = Image.fromarray(final_image)
            final_image = final_image.convert('RGB')

            jpeg_filename = filename.rsplit('.', 1)[0] + '.jpg'
            jpeg_file_path = os.path.join(settings.MEDIA_ROOT, jpeg_filename)
            final_image.save(jpeg_file_path, format='JPEG')

            if os.path.exists(jpeg_file_path):
                jpeg_url = fs.url(jpeg_filename) 
                metadata = extract_metadata(dicom_file)
                return render(request, 'index.html', {'imagen': jpeg_url , 'metadata' : metadata})
            else:
                return render(request, 'index.html', {'error': 'Error al convertir el archivo DICOM a JPEG.'})

        except Exception as e:
            return render(request, 'index.html', {'error': 'No se pudo procesar el archivo DICOM.'})
    return render(request, 'index.html')



def extract_metadata(dicom_file):
    metadata = {}
    for elem in dicom_file:
        if elem.VR != 'SQ':  # Excluir secuencias para simplificar
            metadata[elem.name] = str(elem.value)
    return metadata




