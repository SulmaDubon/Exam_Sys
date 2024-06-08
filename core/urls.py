from django.contrib import admin
from django.urls import path, include
from .views import Homeview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard_users/', include('dashboard_users.urls')),
    path('users/', include('users.urls')),
    path('admin_panel/', include('admin_panel.urls')),
    path('', Homeview.as_view(), name="home"),
]
