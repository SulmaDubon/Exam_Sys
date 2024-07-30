# admin_panel/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from users.models import CustomUser
from dashboard_users.models import Examen, Pregunta
from dashboard_users.forms import ExamenForm, PreguntaForm   # Importar ExamenForm desde admin_panel/forms.py
from users.forms import UserRegistrationForm  # Importar UserRegistrationForm desde users/forms.py
from django.contrib.auth.views import LoginView
from django.contrib import messages 
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse








# from .decorators import es_admin


#-------------------------------------------------------
# Función para verificar si el usuario es administrador
#-------------------------------------------------------
def es_admin(usuario):
    return usuario.is_superuser

#-----------------------------------------------------------
# Login Administrador
#------------------------------------------------------------

#@method_decorator(user_passes_test(es_admin), name='dispatch')
class AdminLoginView(LoginView):
    template_name = 'admin_panel/admin_login.html'

    def get_success_url(self):
        return reverse_lazy('admin_panel:admin_panel')

#-----------------------------------------------------------------
#    ADMIN PANEL
#----------------------------------------------------------------

# Vista principal del panel de administración
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class VistaAdminPanel(View):
    def get(self, request):
        # Renderiza la plantilla principal del panel de administración
        return render(request, 'admin_panel/admin_panel.html')


#-------------------------------------------------------------------
#                 USUARIOS
#--------------------------------------------------------------------

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

# Vista para editar un nuevo usuario
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarUsuario(UpdateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'admin_panel/formulario_usuario.html'
    success_url = reverse_lazy('admin_panel:lista_usuarios')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al actualizar el usuario. Por favor, revisa los datos ingresados.')
        return super().form_invalid(form)

# Vista para eliminar un usuario existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EliminarUsuario(DeleteView):
    model = CustomUser
    template_name = 'admin_panel/confirmar_eliminacion_usuario.html'
    success_url = reverse_lazy('admin_panel:lista_usuarios')
    # Renderiza una página de confirmación y maneja la eliminación del usuario

#------------------------------------------------------------
#                EXAMEN
#-----------------------------------------------------------

# Vista para listar todos los exámenes
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaExamenes(ListView):
    model = Examen
    template_name = 'admin_panel/lista_examenes.html'
    context_object_name = 'examenes'
    paginate_by = 10  # Número de elementos por página

    def get_queryset(self):
        queryset = Examen.objects.all()
        order = self.request.GET.get('order', 'fecha')
        direction = self.request.GET.get('direction', 'asc')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        if year and month:
            queryset = queryset.filter(fecha__year=year, fecha__month=month)
        elif year:
            queryset = queryset.filter(fecha__year=year)
        elif month:
            queryset = queryset.filter(fecha__month=month)
        
        if direction == 'desc':
            order = '-' + order
        
        return queryset.order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.now().year
        current_month = datetime.now().month
        year_list = list(range(current_year - 5, current_year + 5))
        month_list = [
            {'value': i, 'name': datetime(1900, i, 1).strftime('%B')}
            for i in range(1, 13)
        ]
        context['year_list'] = year_list
        context['month_list'] = month_list
        context['current_year'] = self.request.GET.get('year')
        context['current_month'] = self.request.GET.get('month')
        return context

# Vista para crear un nuevo examen
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class CrearExamen(CreateView):
    model = Examen
    form_class = ExamenForm
    template_name = 'admin_panel/formulario_examen.html'
    success_url = reverse_lazy('admin_panel:lista_examenes')

# Vista para editar un examen existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarExamen(UpdateView):
    model = Examen
    form_class = ExamenForm
    template_name = 'admin_panel/formulario_examen.html'
    success_url = reverse_lazy('admin_panel:lista_examenes')

# Vista para eliminar un examen existente
@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EliminarExamen(DeleteView):
    model = Examen
    template_name = 'admin_panel/confirmar_eliminacion_examen.html'
    success_url = reverse_lazy('admin_panel:lista_examenes')


#------------------------------------------------------------------
#     USUARIOS POR EXAMEN
#-----------------------------------------------------------------

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class UsuariosInscritosView(DetailView):
    model = Examen
    template_name = 'admin_panel/usuarios_inscritos.html'
    context_object_name = 'examen'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            usuarios = self.object.usuarios.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(cedula__icontains=search_query)
            )
        else:
            usuarios = self.object.usuarios.all()
        
        paginator = Paginator(usuarios, 20)  # Mostrar 20 usuarios por página
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['search_query'] = search_query
        context['page_obj'] = page_obj
        return context
    
#------------------------------------------------------------------------------
#      PREGUNTAS
#------------------------------------------------------------------------------


@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaPreguntas(ListView):
    model = Pregunta
    template_name = 'admin_panel/lista_preguntas.html'
    context_object_name = 'preguntas'

    def get_queryset(self):
        return Pregunta.objects.all().order_by('orden')
    

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class CrearPregunta(CreateView):
    model = Pregunta
    form_class = PreguntaForm
    template_name = 'admin_panel/formulario_pregunta.html'

    def get_success_url(self):
        return reverse_lazy('admin_panel:lista_preguntas')

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarPregunta(UpdateView):
    model = Pregunta
    form_class = PreguntaForm
    template_name = 'admin_panel/formulario_pregunta.html'

    def get_success_url(self):
        return reverse_lazy('admin_panel:lista_preguntas')

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EliminarPregunta(DeleteView):
    model = Pregunta
    template_name = 'admin_panel/confirmar_eliminacion_pregunta.html'

    def get_success_url(self):
        return reverse_lazy('admin_panel:lista_preguntas')

#------------------------------------------------
#   ACCIONES
#------------------------------------------------
class AccionesExamenesView(View):
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        selected_exams = request.POST.getlist('selected_exams')

        if not selected_exams:
            messages.warning(request, "No se seleccionaron exámenes.")
            return redirect('admin_panel:lista_examenes')

        if action == 'edit':
            if len(selected_exams) > 1:
                messages.warning(request, "Solo puedes editar un examen a la vez.")
                return redirect('admin_panel:lista_examenes')
            return redirect(reverse('admin_panel:editar_examen', args=[selected_exams[0]]))
        
        elif action == 'delete':
            for exam_id in selected_exams:
                exam = get_object_or_404(Examen, id=exam_id)
                exam.delete()
            messages.success(request, "Exámenes eliminados con éxito.")
        
        elif action == 'users':
            if len(selected_exams) > 1:
                messages.warning(request, "Solo puedes ver los usuarios inscritos de un examen a la vez.")
                return redirect('admin_panel:lista_examenes')
            return redirect(reverse('admin_panel:usuarios_inscritos', args=[selected_exams[0]]))

        return redirect('admin_panel:lista_examenes')