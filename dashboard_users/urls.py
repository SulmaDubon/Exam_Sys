# dashboard_users/urls.py

from django.urls import path
from .views import (
    VistaDashboard,
    CambiarContrasena,
    InscripcionExamen,
    ResultadosExamen,
    GenerarExamenView,
    SubmitExamenView
)

app_name = 'dashboard_users'

urlpatterns = [
    path('', VistaDashboard.as_view(), name='dashboard'),
    path('cambiar_contrasena/', CambiarContrasena.as_view(), name='cambiar_contrasena'),
    path('examen/', GenerarExamenView.as_view(), name='generar_examen'),
    path('inscripcion/', InscripcionExamen.as_view(), name='inscripcion'),
    path('resultados/', ResultadosExamen.as_view(), name='resultados'),
    path('submit_examen/', SubmitExamenView.as_view(), name='submit_examen'),
]
