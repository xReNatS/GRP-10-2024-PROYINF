from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import login_view

urlpatterns = [
    path('', login_view, name='login'),  
]
