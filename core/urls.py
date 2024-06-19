
# core/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import Homeview

urlpatterns = [
     path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),  # URLs del usuario
    path('admin_panel/', include('admin_panel.urls', namespace='admin_panel')),  # URLs del panel de administración
    path('dashboard/', include('dashboard_users.urls', namespace='dashboard_users')),  # Incluye las URLs del dashboard
    path('', Homeview.as_view(), name="home"),  # Vista de inicio
]
 