# admin_paner/urls.py

from django.urls import path
from .views import (
    AdminLoginView,
    VistaAdminPanel,
    ListaUsuarios,
    CrearUsuario,
    EditarUsuario,
    EliminarUsuario,
    ListaExamenes,
    CrearExamen,
    EditarExamen,
    EliminarExamen
)

app_name = 'admin_panel'

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),  # URL de inicio de sesión para administradores
    path('', VistaAdminPanel.as_view(), name='admin_panel'),
    path('usuarios/', ListaUsuarios.as_view(), name='lista_usuarios'),
    path('usuarios/crear/', CrearUsuario.as_view(), name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', EditarUsuario.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', EliminarUsuario.as_view(), name='eliminar_usuario'),
    path('examenes/', ListaExamenes.as_view(), name='lista_examenes'),
    path('examenes/crear/', CrearExamen.as_view(), name='crear_examen'),
    path('examenes/editar/<int:pk>/', EditarExamen.as_view(), name='editar_examen'),
    path('examenes/eliminar/<int:pk>/', EliminarExamen.as_view(), name='eliminar_examen'),
]

