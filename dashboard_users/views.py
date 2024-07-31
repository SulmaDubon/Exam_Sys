# dashboard_users/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from .models import Examen, Pregunta, InscripcionExamen
from .forms import ExamenForm
from django.contrib import messages
from django.utils import timezone
import random
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CambiarContrasenaForm
from datetime import datetime, timedelta 
import pytz 
from django.core.paginator import Paginator

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        examen_id = self.kwargs.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        now = timezone.now()

        # Comentar estas líneas para omitir el requisito de fecha y hora
        # local_tz = now.tzinfo
        # inicio_examen = datetime.combine(examen.fecha, examen.hora).replace(tzinfo=local_tz)
        # fin_acceso = inicio_examen + timedelta(minutes=15)
        # fin_examen = inicio_examen + timedelta(hours=1)

        # if inicio_examen <= now <= fin_acceso:
        #     tiempo_restante = (fin_examen - now).total_seconds()
        #     preguntas = Pregunta.objects.filter(examen=examen).order_by('orden')

        #     paginator = Paginator(preguntas, 10)  # 10 preguntas por página
        #     page_number = self.request.GET.get('page')
        #     page_obj = paginator.get_page(page_number)

        #     context['preguntas'] = page_obj
        #     context['examen'] = examen
        #     context['usuario'] = self.request.user
        #     context['tiempo_restante'] = int(tiempo_restante)
        # elif now < inicio_examen:
        #     context['cuenta_regresiva'] = int((inicio_examen - now).total_seconds())
        #     context['mensaje'] = 'El examen estará disponible en:'
        # else:
        #     context['error'] = 'El tiempo de acceso al examen ha expirado.'

        # Lógica sin restricciones de tiempo
        preguntas = Pregunta.objects.filter(examen=examen).order_by('orden')
        paginator = Paginator(preguntas, 10)  # 10 preguntas por página
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['preguntas'] = page_obj
        context['examen'] = examen
        context['usuario'] = self.request.user
        context['tiempo_restante'] = 3600  # 1 hora en segundos para la prueba

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




