from django.contrib import admin
from django.urls import path, include

from .views import Homeview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('exams/', include('exams.urls')),
    path('results/', include('results.urls')),
    path('users/', include('users.urls')),
    path('admin_panel/', include('admin_panel.urls')),
    path('', Homeview.as_view(), name= "home"),
]
