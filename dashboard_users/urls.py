# dashboard_users/urls.py

from django.urls import path
from .views import (
    VistaDashboard,
    CambiarContrasena,
    InscripcionExamenView,  # Actualizar el nombre de la vista de inscripción
    ResultadosExamen,
    GenerarExamenView,
    SubmitExamenView,
    sala_espera_examen
)

app_name = 'dashboard_users'

urlpatterns = [
    path('', VistaDashboard.as_view(), name='dashboard'),
    path('cambiar_contrasena/', CambiarContrasena.as_view(), name='cambiar_contrasena'),
    path('inscripcion/', InscripcionExamenView.as_view(), name='inscripcion'),  # Asegurarse de que el nombre es correcto
    path('examen/<int:examen_id>/', GenerarExamenView.as_view(), name='generar_examen'),
    path('examen/<int:examen_id>/pagina/<int:page>/', GenerarExamenView.as_view(), name='generar_examen'),  # Añadir examen_id
    path('examen/<int:examen_id>/submit/', SubmitExamenView.as_view(), name='submit_examen'),  # Añadir examen_id para el submit
    path('resultados/', ResultadosExamen.as_view(), name='resultados'),
    path('sala_espera/<int:examen_id>/', sala_espera_examen, name='sala_espera_examen'),
]
