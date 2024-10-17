# admin_panel/views.py
from django.forms import ValidationError, formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
import pandas as pd
from users.models import CustomUser
from dashboard_users.models import Examen, Modulo, Pregunta, Respuesta, TipoExamen
from dashboard_users.forms import ExamenForm, PreguntaForm, SubirPreguntasForm, TipoExamenForm, ModuloFormSet, RespuestaFormSet   # Importar ExamenForm desde admin_panel/forms.py
from users.forms import UserRegistrationForm  # Importar UserRegistrationForm desde users/forms.py
from django.contrib.auth.views import LoginView
from django.contrib import messages 
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.db.models import Max
from django.views.generic.edit import FormView
from django.http import JsonResponse


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
#              LISTAR   EXAMEN
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

        # Obtener valores de los parámetros GET o asignar por defecto el año y mes actuales
        selected_year = self.request.GET.get('year', current_year)
        selected_month = self.request.GET.get('month', current_month)

        # Crear listas de años y meses para el filtrado
        year_list = list(range(current_year - 5, current_year + 5))
        month_list = [
            {'value': i, 'name': datetime(1900, i, 1).strftime('%B')}
            for i in range(1, 13)
        ]

        # Actualizar el contexto con los datos necesarios
        context['year_list'] = year_list
        context['month_list'] = month_list
        context['current_year'] = int(selected_year)  # Asegurarse de que sean enteros
        context['current_month'] = int(selected_month)

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

#-------------------------------------------------------
#           VISTA PARA MODULOS ASOCIADOS A EXAMEN
#--------------------------------------------------------

def get_modulos(request, tipo_examen_id):
    # Filtra los módulos por el tipo de examen seleccionado
    modulos = Modulo.objects.filter(tipo_examen_id=tipo_examen_id)
    data = {
        'modulos': [{'id': modulo.id, 'nombre': modulo.nombre} for modulo in modulos]
    }
    return JsonResponse(data)


#------------------------------------------------------------------------------
#      PREGUNTAS
#------------------------------------------------------------------------------

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaPreguntas(ListView):
    model = Pregunta
    template_name = 'admin_panel/lista_preguntas.html'
    context_object_name = 'preguntas'
    paginate_by = 10  # Número de preguntas por página

    def get_queryset(self):
        # Obtener todas las preguntas con sus respuestas relacionadas
        return Pregunta.objects.prefetch_related('respuestas').order_by('id')
        

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')

class CrearPreguntasView(FormView):
    template_name = 'admin_panel/formulario_preguntas.html'
    form_class = PreguntaForm
    success_url = reverse_lazy('admin_panel:lista_preguntas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['respuesta_formset'] = RespuestaFormSet(self.request.POST)
        else:
            context['respuesta_formset'] = RespuestaFormSet()
        return context

    def form_valid(self, form):
        respuesta_formset = RespuestaFormSet(self.request.POST)
        
        if form.is_valid() and respuesta_formset.is_valid():
            # Guardar la pregunta principal (individual o enunciado)
            pregunta = form.save()

            # Si es un enunciado, se manejará a nivel de modelo
            if form.cleaned_data.get('es_enunciado'):
                # Si la pregunta es un enunciado, no necesitamos respuestas inmediatas, pero podrías agregar lógica adicional aquí si es necesario
                pass
            else:
                # Si es una pregunta individual, guardar las respuestas
                respuesta_formset.instance = pregunta
                respuesta_formset.save()
            
            return super().form_valid(form)
        
        # Si algo falla, renderiza el formulario con errores
        return self.form_invalid(form)




@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarPregunta(UpdateView):
    model = Pregunta
    form_class = PreguntaForm
    template_name = 'admin_panel/formulario_pregunta.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = RespuestaFormSet(self.request.POST, instance=self.object)
            context['pregunta_formset'] = PreguntaDerivadaFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = RespuestaFormSet(instance=self.object)
            context['pregunta_formset'] = PreguntaDerivadaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        formset = RespuestaFormSet(self.request.POST, instance=self.object)
        pregunta_formset = PreguntaDerivadaFormSet(self.request.POST, instance=self.object)

        if form.is_valid():
            pregunta = form.save()
            # Si la pregunta tiene un enunciado, actualizamos las preguntas derivadas
            if pregunta.enunciado:
                if pregunta_formset.is_valid():
                    preguntas_derivadas = pregunta_formset.save(commit=False)
                    for pregunta_derivada in preguntas_derivadas:
                        pregunta_derivada.enunciado = pregunta
                        pregunta_derivada.save()
                        # Guardar respuestas para las preguntas derivadas
                        for respuesta_formset in RespuestaFormSet(self.request.POST, instance=pregunta_derivada):
                            if respuesta_formset.is_valid():
                                respuesta_formset.save()
            else:
                if formset.is_valid():
                    formset.save()
            
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('admin_panel:lista_preguntas')



@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EliminarPregunta(DeleteView):
    model = Pregunta
    template_name = 'admin_panel/confirmar_eliminacion_pregunta.html'

    def get_success_url(self):
        return reverse_lazy('admin_panel:lista_preguntas')


def subir_preguntas(request):
    if request.method == 'POST':
        form = SubirPreguntasForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['archivo']
            try:
                df = pd.read_excel(excel_file)

                required_columns = ['texto', 'respuesta_correcta', 'respuesta1', 'respuesta2', 'respuesta3']
                if 'enunciado' in df.columns:
                    required_columns.append('enunciado')

                if not all(column in df.columns for column in required_columns):
                    raise ValidationError("El archivo Excel debe contener las columnas correctas.")

                max_orden = Pregunta.objects.aggregate(Max('orden'))['orden__max'] or 0

                for _, row in df.iterrows():
                    if 'enunciado' in row and pd.notna(row['enunciado']):
                        enunciado, created = Pregunta.objects.get_or_create(texto=row['enunciado'], es_enunciado=True)
                        pregunta = Pregunta.objects.create(texto=row['texto'], orden=max_orden + 1, enunciado=enunciado)
                    else:
                        pregunta = Pregunta.objects.create(texto=row['texto'], orden=max_orden + 1)

                    respuestas = [
                        {'texto': row['respuesta1'], 'es_correcta': row['respuesta_correcta'] == row['respuesta1']},
                        {'texto': row['respuesta2'], 'es_correcta': row['respuesta_correcta'] == row['respuesta2']},
                        {'texto': row['respuesta3'], 'es_correcta': row['respuesta_correcta'] == row['respuesta3']},
                    ]
                    for respuesta_data in respuestas:
                        Respuesta.objects.create(pregunta=pregunta, **respuesta_data)
                    max_orden += 1

                return redirect(reverse('admin_panel:lista_preguntas'))
            except Exception as e:
                form.add_error(None, f"Error procesando el archivo: {str(e)}")
    else:
        form = SubirPreguntasForm()
    return render(request, 'admin_panel/subir_preguntas.html', {'form': form})


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


#---------------------------------------------
#             CREAR TIPO EXAMEN
#----------------------------------------------

class TipoExamenListView(ListView):
    model = TipoExamen
    template_name = 'admin_panel/lista_tipo_examen.html'
    context_object_name = 'tipos_examenes'

    def get_queryset(self):
        # Utilizamos prefetch_related para traer todos los módulos relacionados en una sola operación
        return TipoExamen.objects.prefetch_related('modulos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Preparar información de módulos para cada tipo de examen
        tipos_examenes_info = []
        for tipo_examen in context['tipos_examenes']:
            # `tipo_examen.modulos.all()` usa los módulos prefetched gracias a `prefetch_related`
            modulos = tipo_examen.modulos.all()
            total_preguntas = sum(modulo.cantidad_preguntas for modulo in modulos)
            
            tipos_examenes_info.append({
                'tipo_examen': tipo_examen,
                'modulos': modulos,
                'total_preguntas': total_preguntas
            })

        # Añadir la información enriquecida al contexto
        context['tipos_examenes_info'] = tipos_examenes_info
        return context



class CrearTipoExamenView(View):
    def get(self, request):
        tipo_examen_form = TipoExamenForm()
        modulo_formset = ModuloFormSet()
        context = {
            'tipo_examen_form': tipo_examen_form,
            'modulo_formset': modulo_formset
        }
        return render(request, 'admin_panel/crear_tipo_examen.html', context)

    def post(self, request):
        tipo_examen_form = TipoExamenForm(request.POST)
        modulo_formset = ModuloFormSet(request.POST)

        if tipo_examen_form.is_valid() and modulo_formset.is_valid():
            tipo_examen = tipo_examen_form.save()
            modulo_formset.instance = tipo_examen
            modulo_formset.save()
            return redirect('admin_panel:lista_tipo_examen')  # Cambia 'ruta_donde_redirigir' a la URL de listar

        context = {
            'tipo_examen_form': tipo_examen_form,
            'modulo_formset': modulo_formset
        }
        return render(request, 'admin_panel/crear_tipo_examen.html', context)




class EditarTipoExamenView(View):
    def get(self, request, pk):
        tipo_examen = get_object_or_404(TipoExamen, pk=pk)
        tipo_examen_form = TipoExamenForm(instance=tipo_examen)
        modulo_formset = ModuloFormSet(instance=tipo_examen)
        context = {
            'tipo_examen_form': tipo_examen_form,
            'modulo_formset': modulo_formset
        }
        return render(request, 'editar_tipo_examen.html', context)

    def post(self, request, pk):
        tipo_examen = get_object_or_404(TipoExamen, pk=pk)
        tipo_examen_form = TipoExamenForm(request.POST, instance=tipo_examen)
        modulo_formset = ModuloFormSet(request.POST, instance=tipo_examen)

        if tipo_examen_form.is_valid() and modulo_formset.is_valid():
            tipo_examen = tipo_examen_form.save()
            modulo_formset.save()
            return redirect('ruta_donde_redirigir')

        context = {
            'tipo_examen_form': tipo_examen_form,
            'modulo_formset': modulo_formset
        }
        return render(request, 'editar_tipo_examen.html', context)
    

class TipoExamenDeleteView(DeleteView):
    model = TipoExamen
    template_name = 'admin_panel/confirmar_eliminar_tipo_examen.html'
    success_url = reverse_lazy('admin_panel:listar_tipo_examen')  # Redirige a la lista de exámenes después de eliminar


