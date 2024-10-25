from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.upload_file, name='app'),
    path('info/', views.upload_info_view, name='info'),
]
