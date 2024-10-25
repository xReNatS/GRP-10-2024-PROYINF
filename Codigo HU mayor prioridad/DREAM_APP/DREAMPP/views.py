from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import numpy as np
import pydicom
import os
from django.conf import settings

def upload_file(request):
    jpeg_url = None
    metadata = {}
    original_metadata = {}
    show_image = True 

    # Verificar si se subió un archivo
    if request.method == 'POST' and request.FILES.get('archivo_dicom'):
        archivo_dicom = request.FILES['archivo_dicom']
        fs = FileSystemStorage()

        filename = fs.save(archivo_dicom.name, archivo_dicom)
        file_absolute_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            dicom_file = pydicom.dcmread(file_absolute_path)
            image_array = dicom_file.pixel_array.astype(float)

            # Procesar la imagen
            rescaled_image = (np.maximum(image_array, 0) / image_array.max()) * 255
            final_image = np.uint8(rescaled_image)

            final_image = Image.fromarray(final_image)
            final_image = final_image.convert('RGB')

            # Guardar la imagen en formato JPEG
            jpeg_filename = filename.rsplit('.', 1)[0] + '.jpg'
            jpeg_file_path = os.path.join(settings.MEDIA_ROOT, jpeg_filename)
            final_image.save(jpeg_file_path, format='JPEG')

            # Verificar si el archivo JPEG se guardó
            if os.path.exists(jpeg_file_path):
                jpeg_url = fs.url(jpeg_filename)
                metadata = extract_metadata(dicom_file)
                original_metadata = metadata.copy()

                # Guardar la información en la sesión
                request.session['dicom_image'] = jpeg_url
                request.session['dicom_metadata'] = original_metadata

        except Exception as e:
            return render(request, 'index.html', {'error': 'No se pudo procesar el archivo DICOM.'})

    else:
        jpeg_url = request.session.get('dicom_image')
        original_metadata = request.session.get('dicom_metadata', {})

    search_query = request.GET.get('search', '')

    # filtrar datos
    metadata = original_metadata
    if search_query:
        metadata = {k: v for k, v in original_metadata.items() if search_query.lower() in k.lower() or search_query.lower() in str(v).lower()}


    # Renderizar la plantilla con la imagen datos filtrados y datos originales
    return render(request, 'index.html', {
        'imagen': jpeg_url, # Solo mostrar la imagen si show_image es verdadero
        'metadata': metadata,
        'original_metadata': original_metadata,
        'search_query': search_query
    })

def extract_metadata(dicom_file):
    metadata = {}
    for elem in dicom_file:
        if elem.VR != 'SQ': 
            metadata[elem.name] = str(elem.value)
    return metadata


def upload_info_view(request):
    metadata = {}
    original_metadata = {}

    # Verificar si se subió un archivo
    if request.method == 'POST' and request.FILES.get('archivo_dicom'):
        archivo_dicom = request.FILES['archivo_dicom']
        fs = FileSystemStorage()

        filename = fs.save(archivo_dicom.name, archivo_dicom)
        file_absolute_path = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            dicom_file = pydicom.dcmread(file_absolute_path)
            metadata = extract_metadata(dicom_file)
            original_metadata = metadata.copy()

            # Guardar la información en la sesión
            request.session['dicom_metadata'] = original_metadata

        except Exception as e:
            return render(request, 'info.html', {'error': 'No se pudo procesar el archivo DICOM.'})

    # Intentar cargar datos desde la sesión
    else:
        original_metadata = request.session.get('dicom_metadata', {})

    # Filtrar "Pixel data" del diccionario original_metadata
    filtered_metadata = {k: v for k, v in original_metadata.items() if 'Pixel Data' not in k}

    # Manejar la búsqueda de datos
    search_query = request.GET.get('search', '')

    # Filtrar datos si hay una búsqueda
    metadata = filtered_metadata
    if search_query:
        metadata = {k: v for k, v in filtered_metadata.items() if search_query.lower() in k.lower() or search_query.lower() in str(v).lower()}

    return render(request, 'info.html', {
        'metadata': metadata,
        'original_metadata': filtered_metadata,  
        'search_query': search_query
    })


