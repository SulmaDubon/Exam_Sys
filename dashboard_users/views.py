# dashboard_users/views.py

from datetime import timedelta
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
from .forms import CambiarContrasenaForm
from django.core.paginator import Paginator
from .tasks import preparar_examenes  # Asegúrate de que esta línea está presente
from celery.result import AsyncResult




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

#----------------------------------------
#   EXAMEN
#-----------------------------------------

class GenerarExamenView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/examen.html'

    def get(self, request, *args, **kwargs):
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        usuario = request.user

        # Verificar si ya existe un examen para el usuario
        user_exam, created = UserExam.objects.get_or_create(usuario=usuario, examen=examen)

        if created:
            # Selección aleatoria de preguntas
            total_preguntas = Pregunta.objects.count()
            preguntas_a_mostrar = min(200, total_preguntas)
            preguntas = list(Pregunta.objects.order_by('?')[:preguntas_a_mostrar])
            user_exam.preguntas.set(preguntas)

        # Calcular tiempo restante
        now = timezone.now()
        tiempo_transcurrido = (now - user_exam.inicio).total_seconds()
        tiempo_restante = max(0, 3600 - tiempo_transcurrido)  # 1 hora en segundos

        if tiempo_restante <= 0:
            user_exam.finalizado = True
            user_exam.save()
            return redirect('dashboard_users:examen_expirado')

        context = self.get_context_data(
            examen=examen,
            usuario=usuario,
            preguntas=user_exam.preguntas.all(),
            tiempo_restante=tiempo_restante
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preguntas = kwargs.get('preguntas', Pregunta.objects.none())
        paginator = Paginator(preguntas, 20)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['examen'] = kwargs.get('examen')
        context['usuario'] = kwargs.get('usuario')
        tiempo_restante = kwargs.get('tiempo_restante', 0)
        context['tiempo_restante'] = int(tiempo_restante)

        return context


    
    




class ProgramarPreparacionExamenView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        
        # Programar la tarea de Celery para preparar los exámenes
        task = preparar_examenes.apply_async((examen.id,), eta=examen.fecha_hora_inicio)
        
        return render(request, 'dashboard_users/preparacion_programada.html', {
            'examen': examen,
            'task_id': task.id
        })


class ExamenGenerandoView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/examen_generando.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_id'] = self.kwargs.get('task_id')
        return context

class ExamenExpiradoView(TemplateView):
    template_name = 'dashboard_users/examen_expirado.html'



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
        messages.success(request, resultado)
        return redirect('dashboard_users:resultados')


#---------------------------------
# INSCRIPCION
#---------------------------------

class InscripcionExamenView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/inscripcion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['examenes'] = Examen.objects.filter(fecha__gt=now.date()) | Examen.objects.filter(fecha=now.date(), hora__gt=now.time())
        return context

    def post(self, request, *args, **kwargs):
        examen_id = request.POST.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        inscripcion, created = InscripcionExamen.objects.get_or_create(usuario=request.user, examen=examen)
        if created:
            messages.success(request, 'Te has inscrito exitosamente al examen.')
        else:
            messages.info(request, 'Ya estás inscrito en este examen.')
        return HttpResponseRedirect(reverse('dashboard_users:dashboard'))



#------------------------------
#   Resultados
#------------------------------

class ResultadosExamen(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/resultados.html'




