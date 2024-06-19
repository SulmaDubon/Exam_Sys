# admin_panel/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from users.models import CustomUser
from .models import Examen
from admin_panel.forms import ExamenForm   # Importar ExamenForm desde admin_panel/forms.py
from users.forms import UserRegistrationForm  # Importar UserRegistrationForm desde users/forms.py
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test


# Función para verificar si el usuario es administrador
def es_admin(usuario):
    return usuario.is_superuser

#@method_decorator(user_passes_test(es_admin), name='dispatch')
class AdminLoginView(LoginView):
    template_name = 'admin_panel/admin_login.html'

    def get_success_url(self):
        return reverse_lazy('admin_panel:admin_panel')

# Vista principal del panel de administración
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class VistaAdminPanel(View):
    def get(self, request):
        # Renderiza la plantilla principal del panel de administración
        return render(request, 'admin_panel/admin_panel.html')

# Vista para listar todos los usuarios
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaUsuarios(ListView):
    model = CustomUser
    template_name = 'admin_panel/lista_usuarios.html'
    context_object_name = 'usuarios'
    # Renderiza la plantilla con la lista de usuarios

# Vista para crear un nuevo usuario
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class CrearUsuario(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'admin_panel/formulario_usuario.html'
    success_url = reverse_lazy('admin_panel:lista_usuarios')
    # Renderiza el formulario para crear un usuario y maneja su creación

# Vista para editar un usuario existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarUsuario(UpdateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'admin_panel/formulario_usuario.html'
    success_url = reverse_lazy('admin_panel:lista_usuarios')
    # Renderiza el formulario para editar un usuario y maneja su actualización

# Vista para eliminar un usuario existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EliminarUsuario(DeleteView):
    model = CustomUser
    template_name = 'admin_panel/confirmar_eliminacion_usuario.html'
    success_url = reverse_lazy('admin_panel:lista_usuarios')
    # Renderiza una página de confirmación y maneja la eliminación del usuario

# Vista para listar todos los exámenes
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaExamenes(ListView):
    model = Examen
    template_name = 'admin_panel/lista_examenes.html'
    context_object_name = 'examenes'
    # Renderiza la plantilla con la lista de exámenes

# Vista para crear un nuevo examen
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class CrearExamen(CreateView):
    model = Examen
    form_class = ExamenForm
    template_name = 'admin_panel/formulario_examen.html'
    success_url = reverse_lazy('admin_panel:lista_examenes')
    # Renderiza el formulario para crear un examen y maneja su creación

# Vista para editar un examen existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarExamen(UpdateView):
    model = Examen
    form_class = ExamenForm
    template_name = 'admin_panel/formulario_examen.html'
    success_url = reverse_lazy('admin_panel:lista_examenes')
    # Renderiza el formulario para editar un examen y maneja su actualización

# Vista para eliminar un examen existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EliminarExamen(DeleteView):
    model = Examen
    template_name = 'admin_panel/confirmar_eliminacion_examen.html'
    success_url = reverse_lazy('admin_panel:lista_examenes')
    # Renderiza una página de confirmación y maneja la eliminación del examen
