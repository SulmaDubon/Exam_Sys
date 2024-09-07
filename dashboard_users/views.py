# dashboard_users/views.py

from datetime import timedelta
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
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

from django.http import HttpResponseForbidden

class GenerarExamenView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/examen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)

        # Selección aleatoria de preguntas
        total_preguntas = Pregunta.objects.filter(examen=examen).count()
        preguntas_a_mostrar = min(10, total_preguntas)  # Mostrar hasta 10 preguntas al azar
        preguntas = Pregunta.objects.filter(examen=examen).order_by('?')[:preguntas_a_mostrar]

        paginator = Paginator(preguntas, 10)  # Paginación por página
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['preguntas'] = page_obj
        context['examen'] = examen
        context['usuario'] = self.request.user

        return context

    def post(self, request, *args, **kwargs):
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        usuario = request.user

        # Verificar si el usuario ya tiene un examen iniciado
        user_exam, created = UserExam.objects.get_or_create(
            usuario=usuario,
            examen=examen,
            defaults={'inicio': timezone.now(), 'finalizacion': timezone.now() + timedelta(hours=3, minutes=30), 'finalizado': False}
        )

        if created:
            user_exam.save()

        return redirect('examen_preguntas', examen_id=examen_id)

    def post_enviar_examen(self, request, *args, **kwargs):
        examen_id = self.kwargs.get('examen_id')
        user_exam = get_object_or_404(UserExam, usuario=request.user, examen_id=examen_id)

        # Verificar si user_exam.finalizacion no es None antes de la comparación
        if user_exam.finalizacion and timezone.now() >= user_exam.finalizacion:
            # Lógica para guardar respuestas y finalizar el examen
            user_exam.finalizado = True
            user_exam.save()
            return redirect('examen_finalizado', examen_id=examen_id)
        else:
            return HttpResponseForbidden("El examen no ha terminado aún.")




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




