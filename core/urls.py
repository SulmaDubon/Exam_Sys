
# core/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import Homeview

urlpatterns = [
    path('admin/', admin.site.urls),  # URLs del sitio de administración
    path('dashboard_users/', include('dashboard_users.urls')),  # Incluye URLs de la app dashboard_users
    path('users/', include('users.urls')),  # Incluye URLs de la app users
    path('admin_panel/', include('admin_panel.urls')),  # Incluye URLs de la app admin_panel
    path('', Homeview.as_view(), name="home"),  # Vista de inicio
]
 