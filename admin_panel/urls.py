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
    EliminarExamen,
    UsuariosInscritosView,
    ListaPreguntas,
    CrearPreguntasView,
    EditarPregunta,
    EliminarPregunta,
    AccionesExamenesView,
    subir_preguntas, 
    crear_tipo_examen     
)

app_name = 'admin_panel'

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('', VistaAdminPanel.as_view(), name='admin_panel'),
    path('usuarios/', ListaUsuarios.as_view(), name='lista_usuarios'),
    path('usuarios/crear/', CrearUsuario.as_view(), name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', EditarUsuario.as_view(), name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', EliminarUsuario.as_view(), name='eliminar_usuario'),
    path('examenes/', ListaExamenes.as_view(), name='lista_examenes'),
    path('examenes/crear/', CrearExamen.as_view(), name='crear_examen'),
    path('examenes/editar/<int:pk>/', EditarExamen.as_view(), name='editar_examen'),
    path('examenes/eliminar/<int:pk>/', EliminarExamen.as_view(), name='eliminar_examen'),
    path('examenes/usuarios-inscritos/<int:pk>/', UsuariosInscritosView.as_view(), name='usuarios_inscritos'),
    path('preguntas/', ListaPreguntas.as_view(), name='lista_preguntas'),
    path('preguntas/crear/', CrearPreguntasView.as_view(), name='crear_pregunta'),
    path('preguntas/editar/<int:pk>/', EditarPregunta.as_view(), name='editar_pregunta'),
    path('preguntas/eliminar/<int:pk>/', EliminarPregunta.as_view(), name='eliminar_pregunta'),
    path('preguntas/subir/', subir_preguntas, name='subir_preguntas'),  # Añadir esta línea para la vista de subir preguntas
    path('examenes/acciones/', AccionesExamenesView.as_view(), name='acciones_examenes'),
    path('crear-tipo-examen/', crear_tipo_examen, name='crear_tipo_examen'),
]
