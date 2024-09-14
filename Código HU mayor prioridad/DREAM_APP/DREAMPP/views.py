from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import pydicom
import io
import os
from django.conf import settings

def mi_vista(request):
    if request.method == 'POST' and request.FILES.get('archivo_dicom'):
        archivo = request.FILES['archivo_dicom']
        fs = FileSystemStorage()
        nombre_archivo = fs.save(archivo.name, archivo)
        ruta_archivo = fs.url(nombre_archivo)
        
        return render(request, 'DREAMPP/index.html', {'imagen': ruta_archivo})
    return render(request, 'DREAMPP/index.html')


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('archivo_dicom'):
        archivo_dicom = request.FILES['archivo_dicom']
        fs = FileSystemStorage()

        filename = fs.save(archivo_dicom.name, archivo_dicom)
        file_path = fs.url(filename).strip('/')
        file_absolute_path = os.path.join(settings.MEDIA_ROOT, filename)

        dicom_file = pydicom.dcmread(file_absolute_path)
        image_array = dicom_file.pixel_array
        
        image = Image.fromarray(image_array)
        image = image.convert('RGB') 

        jpeg_filename = filename.rsplit('.', 1)[0] + '.jpg'
        jpeg_file_path = os.path.join(settings.MEDIA_ROOT, jpeg_filename)
        image.save(jpeg_file_path, format='JPEG')

        if os.path.exists(jpeg_file_path):
            jpeg_url = fs.url(jpeg_filename)
            return render(request, 'upload.html', {'imagen': jpeg_url})
        else:
            return render(request, 'upload.html', {'error': 'Error al convertir el archivo DICOM a JPEG'})
    
    return render(request, 'upload.html')

