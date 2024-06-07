from django.contrib import admin
from django.urls import path, include

from .views import Homeview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  # Incluye las rutas de la aplicación users
    path('', Homeview.as_view(), name= "home"),
]
