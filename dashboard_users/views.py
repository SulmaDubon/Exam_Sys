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

class GenerarExamenView(TemplateView):
    template_name = 'dashboard_users/examen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        usuario = self.request.user

        # Verifica si ya tiene un examen generado
        user_exam, created = UserExam.objects.get_or_create(
            usuario=usuario,
            examen=examen,
            defaults={'inicio': timezone.now()}
        )

        # Selección de 260 preguntas al azar
        if created:
            preguntas = Pregunta.objects.order_by('?')[:260]
            user_exam.preguntas.set(preguntas)
        else:
            # Actualiza el tiempo restante
            tiempo_maximo = 3 * 60 * 60  # 3 horas en segundos
            tiempo_transcurrido = (timezone.now() - user_exam.inicio).total_seconds()
            if tiempo_transcurrido >= tiempo_maximo:
                # Marca el examen como finalizado si el tiempo se agotó
                user_exam.examen_finalizado()
                return redirect('dashboard_users:dashboard')  # Redirige al dashboard

        # Paginación
        page_number = self.request.GET.get('page', 1)  # Página actual
        paginator = Paginator(user_exam.preguntas.all(), 20)  # 20 preguntas por página
        page_obj = paginator.get_page(page_number)

        context['examen'] = examen
        context['usuario'] = usuario
        context['preguntas'] = page_obj
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        context['tiempo_restante'] = int(max(0, 3 * 60 * 60 - (timezone.now() - user_exam.inicio).total_seconds()))
        return context



class SubmitExamenView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        inscripcion = get_object_or_404(InscripcionExamen, examen=examen, usuario=request.user)

        puntaje = 0
        total_preguntas = 0
        for key, value in request.POST.items():
            if key.startswith('pregunta_'):
                pregunta_id = int(key.split('_')[1])
                respuesta_seleccionada = value
                pregunta = Pregunta.objects.get(id=pregunta_id)
                if respuesta_seleccionada == pregunta.respuesta_correcta:
                    puntaje += 1
                total_preguntas += 1
        
        resultado = f"Puntaje: {puntaje}/{total_preguntas}"
        inscripcion.resultado = resultado
        inscripcion.save()

        messages.success(request, "El examen se ha enviado exitosamente.")
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




