import base64
import io
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image, ImageEnhance, ImageOps
import numpy as np
import pydicom
import os
from django.conf import settings

def upload_file(request):
    jpeg_url = None
    metadata = {}

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

                # Guardar la información en la sesión
                request.session['dicom_image'] = jpeg_url
                request.session['dicom_metadata'] = metadata

        except Exception as e:
            return render(request, 'index.html', {'error': 'No se pudo procesar el archivo DICOM.'})


    # Renderizar la plantilla con la imagen y los metadatos
    return render(request, 'index.html', {
        'imagen': jpeg_url,
        'metadata': metadata,
    })


def extract_metadata(dicom_file):
    metadata = {}
    for elem in dicom_file:
        if elem.VR != 'SQ' and elem.VR != 'PixelData': 
            metadata[elem.name] = str(elem.value)
    return metadata


def view_header(request):
    
    dicom_file_path = request.session.get('dicom_file_path')  

    if not dicom_file_path:
        return render(request, 'error.html', {'message': 'No DICOM file found in session'})

    ds = pydicom.dcmread(dicom_file_path)

    dicom_data = {}

    fields_of_interest = {
        'Patient ID': (0x0010, 0x0020),
        'Patient Name': (0x0010, 0x0010),
        'Patient Birth Date': (0x0010, 0x0030),
        'Patient Sex': (0x0010, 0x0040),
        'Study Date': (0x0008, 0x0020),
        'Study Time': (0x0008, 0x0030),
        'Study Instance UID': (0x0020, 0x000D),
        'Series Instance UID': (0x0020, 0x000E),
        'Modality': (0x0008, 0x0060),
        'Series Date': (0x0008, 0x0021),
        'Image Position': (0x0020, 0x0032),
        'Image Orientation': (0x0020, 0x0037),
        'Slice Thickness': (0x0018, 0x0050),
        'Repetition Time': (0x0018, 0x0080),
        'Echo Time': (0x0018, 0x0081),
        'Protocol Name': (0x0018, 0x1030),
        'Manufacturer': (0x0008, 0x0070),
        'Study Description': (0x0008, 0x1030),
        'Series Description': (0x0008, 0x103E),
        'Convolution Kernel': (0x0018, 0x1210),
    }

    
    for field_name, tag in fields_of_interest.items():
        if tag in ds:
            dicom_data[field_name] = ds.get(tag).value
    
    search_query = request.GET.get('search', '').lower()

    # Filtra los resultados según el término de búsqueda
    if search_query:
        dicom_data = {key: value for key, value in dicom_data.items() if search_query in key.lower()}

    # Renderizar la plantilla con los datos
    return render(request, 'dicom_header.html', {'dicom_data': dicom_data, 'search_query': search_query})


def apply_filters(request):
    jpeg_url = request.GET.get('jpeg_url')
    contrast_value = float(request.GET.get('contrast', 1.0))
    negative = request.GET.get('negative', 'false') == 'true'
    colormap = request.GET.get('colormap', '')
    
    # Abrir la imagen JPEG original
    if jpeg_url:
        jpeg_path = os.path.join(settings.MEDIA_ROOT, jpeg_url.strip("/"))
    else:
        return JsonResponse({'error': 'URL de imagen no válida'}, status=400)
    
    # Aplicar los filtros
    try:
        with Image.open(jpeg_path) as image:
            if contrast_value != 1.0:
                image = ImageEnhance.Contrast(image).enhance(contrast_value)

            if negative:
                image = ImageOps.invert(image.convert("RGB"))

            if colormap == 'gray':
                image = image.convert('L')  # Escala de grises
            elif colormap == 'sepia':
                sepia_filter = [(255, 240, 192)]  # Sepia simplificado
                image = ImageOps.colorize(image.convert('L'), 'black', 'brown')

    # Convertir la imagen procesada a base64 para actualizar en tiempo real
            image_io = io.BytesIO()
            image.save(image_io, format='PNG')
            image_io.seek(0)
            image_data_base64 = base64.b64encode(image_io.read()).decode('utf-8')

            return JsonResponse({'image_data': image_data_base64})
    
    except FileNotFoundError:
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)