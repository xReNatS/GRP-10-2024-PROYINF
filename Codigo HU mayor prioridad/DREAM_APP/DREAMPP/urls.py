from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.upload_file, name='app'),
    path('dicom-header/', views.view_header, name='dicom_header'),
    path('apply-filters/', views.apply_filters, name='apply_filters')
]
