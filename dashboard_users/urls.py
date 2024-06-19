# dashboard_users/urls.py

from django.urls import path
from .views import (
    VistaDashboard,
    CambiarContrasena,
    VistaExamen,
    InscripcionExamen,
    ResultadosExamen
)

app_name = 'dashboard_users'

urlpatterns = [
    path('', VistaDashboard.as_view(), name='dashboard'),
    path('cambiar_contrasena/', CambiarContrasena.as_view(), name='cambiar_contrasena'),
    path('examen/', VistaExamen.as_view(), name='examen'),
    path('inscripcion/', InscripcionExamen.as_view(), name='inscripcion'),
    path('resultados/', ResultadosExamen.as_view(), name='resultados'),
]
