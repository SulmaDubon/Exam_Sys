
# core/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import HomeView, AboutView, ContactView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name="home"),
    path('users/', include('users.urls', namespace='users')),  # URLs del usuario
    path('admin_panel/', include('admin_panel.urls', namespace='admin_panel')),  # URLs del panel de administración
    path('dashboard/', include('dashboard_users.urls', namespace='dashboard_users')),  # Incluye las URLs del dashboard
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    
]
 