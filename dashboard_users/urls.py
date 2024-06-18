#dashboard/urls.py
from django.urls import path
from .views import dashboard, inscripcion, examen, resultados, cambiar_contrasena

app_name = 'dashboard_users'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('inscripcion/', inscripcion, name='inscripcion'),
    path('examen/', examen, name='examen'),
    path('resultados/', resultados, name='resultados'),
    path('cambiar_contrasena/', cambiar_contrasena, name='cambiar_contrasena'),
]
