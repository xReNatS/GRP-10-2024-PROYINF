from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [

    path("favicon.ico", lambda request: HttpResponse(status=204)),

    path('', views.upload_file, name='app'),
    path('dicom-header/', views.view_header, name='dicom_header'),
    path('apply-filters/', views.apply_filters, name='apply_filters'),
    path('process-measurement/', views.process_measurement, name='process_measurement'),
    
                                      
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
