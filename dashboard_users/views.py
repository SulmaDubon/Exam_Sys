# dashboard_users/views.py

from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Examen, Pregunta, InscripcionExamen, UserExam
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CambiarContrasenaForm, InscripcionExamenForm
from django.core.paginator import Paginator
from django.db.models import Q


#------------------------------
#   DASHBOARD
#-------------------------------



class VistaDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['usuario'] = user
        context['examenes_inscritos'] = InscripcionExamen.objects.filter(usuario=user)
        return context
    
#----------------------------------
#   CONTRASEÑA
#-----------------------------------

class CambiarContrasena(LoginRequiredMixin, View):
    form_class = CambiarContrasenaForm
    template_name = 'dashboard_users/cambiar_contrasena.html'

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contraseña cambiada con éxito.')
            return redirect('dashboard_users:dashboard')
        messages.error(request, 'Por favor corrige los errores a continuación.')
        return render(request, self.template_name, {'form': form})


#-----------------------------------------------
#      SALA DE ESPERA
#-----------------------------------------------
def sala_espera_examen(request, examen_id):
    # Obtener el examen por su ID
    examen = get_object_or_404(Examen, id=examen_id)
    
    # Obtener la fecha y hora del examen y asegurarse de que es timezone-aware
    examen_datetime = datetime.combine(examen.fecha, examen.hora)
    examen_datetime = timezone.make_aware(examen_datetime, timezone.get_current_timezone())

    # Obtener la hora actual y asegurarse de que es timezone-aware
    ahora = timezone.now()

    # Calcular el tiempo restante
    tiempo_restante = examen_datetime - ahora

    # Si ya es la hora del examen, redirigir al examen
    if tiempo_restante <= timedelta(0):
        return redirect('dashboard_users:generar_examen', examen_id=examen.id)

    # Si falta tiempo para el examen, mostrar la sala de espera
    context = {
        'examen': examen,
        'tiempo_restante': tiempo_restante
    }
    return render(request, 'dashboard_users/sala_espera.html', context)



#----------------------------------------
#   EXAMEN
#-----------------------------------------
class GenerarExamenView(View):
    template_name = 'dashboard_users/examen.html'

    def get(self, request, examen_id, page=1):
        user_exam = get_object_or_404(UserExam, examen_id=examen_id, usuario=request.user)

        # Verificar si el examen ya fue finalizado
        if user_exam.finalizado:
            messages.info(request, 'Este examen ya ha sido completado.')
            return redirect('dashboard_users:resultados')

        # Obtener las preguntas del examen del usuario y paginarlas
        preguntas = user_exam.preguntas.all()
        paginator = Paginator(preguntas, 20)  # Mostrar 20 preguntas por página
        pagina_actual = paginator.get_page(page)

        context = {
            'user_exam': user_exam,
            'pagina_actual': pagina_actual,
            'nombre_examen': user_exam.examen.nombre,
            'nombre_usuario': f"{request.user.first_name} {request.user.last_name}",
            'cedula': request.user.cedula,
            'correo': request.user.email,
            'modulo_actual': pagina_actual.object_list[0].modulo if pagina_actual.object_list else None,
        }

        return render(request, self.template_name, context)

    def post(self, request, examen_id, page=1):
        user_exam = get_object_or_404(UserExam, examen_id=examen_id, usuario=request.user)

        # Verificar si el examen ya fue finalizado
        if user_exam.finalizado:
            messages.error(request, 'Este examen ya ha sido completado.')
            return redirect('dashboard_users:resultados')

        # Guardar las respuestas enviadas para las preguntas de la página actual
        pagina_actual = Paginator(user_exam.preguntas.all(), 20).get_page(page)
        for pregunta in pagina_actual:
            respuesta_usuario = request.POST.get(f'respuesta_{pregunta.id}', None)
            if respuesta_usuario:
                user_exam.respuestas[str(pregunta.id)] = respuesta_usuario

        user_exam.save()

        # Verificar si el usuario presionó el botón de finalizar
        if 'finalizar' in request.POST:
            user_exam.examen_finalizado()
            user_exam.calcular_nota()
            messages.success(request, 'Has completado el examen.')
            return redirect('dashboard_users:resultados')

        # Verificar si el usuario presionó "anterior" o "siguiente"
        if 'anterior' in request.POST and pagina_actual.has_previous():
            return redirect('dashboard_users:generar_examen', examen_id=user_exam.id, page=pagina_actual.previous_page_number())
        elif 'siguiente' in request.POST and pagina_actual.has_next():
            return redirect('dashboard_users:generar_examen', examen_id=user_exam.id, page=pagina_actual.next_page_number())

        # Redirigir al dashboard si algo sale mal
        return redirect('dashboard_users:dashboard')





#---------------------------------
# INSCRIPCION
#---------------------------------

class InscripcionExamenView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/inscripcion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar el formulario con el usuario actual
        context['form'] = InscripcionExamenForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        # Pasar el usuario al formulario para manejar la lógica de validación
        form = InscripcionExamenForm(request.POST, user=request.user)
        if form.is_valid():
            examen = form.cleaned_data['examen']
            inscripcion, created = InscripcionExamen.objects.get_or_create(usuario=request.user, examen=examen)

            if created:
                # Crear una instancia de UserExam después de inscribirse
                preguntas_examen = examen.preguntas.all()
                user_exam = UserExam.objects.create(usuario=request.user, examen=examen)
                user_exam.preguntas.set(preguntas_examen)
                user_exam.save()

                messages.success(request, 'Te has inscrito exitosamente al examen.')
            else:
                messages.info(request, 'Ya estás inscrito en este examen.')

            # Redirigir al dashboard después de la inscripción
            return HttpResponseRedirect(reverse('dashboard_users:dashboard'))
        else:
            # Mostrar mensaje de error en caso de un formulario inválido
            messages.error(request, 'Ha ocurrido un error al inscribirte en el examen.')
            # Renderizar la misma página con el formulario inválido y sus errores
            return self.render_to_response(self.get_context_data(form=form))
          
        
#------------------------------
#   Resultados
#------------------------------

class ResultadosExamen(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/resultados.html'




