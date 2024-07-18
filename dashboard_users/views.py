# dashboard_users/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from .models import Examen, Pregunta
from .forms import ExamenForm
from django.contrib import messages
from django.utils import timezone
import random
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CambiarContrasenaForm

#------------------------------
#   DASHBOARD
#-------------------------------

class VistaDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        ahora = timezone.now()
        context['usuario'] = user
        context['examenes_inscritos'] = Examen.objects.filter(inscripcionexamen__usuario=user, fecha__gte=ahora.date()).exclude(fecha=ahora.date(), hora__lte=ahora.time())
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
        todas_las_preguntas = list(Pregunta.objects.all())
        preguntas_seleccionadas = random.sample(todas_las_preguntas, min(len(todas_las_preguntas), 100))
        context['preguntas'] = preguntas_seleccionadas
        return context

class SubmitExamenView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
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
        messages.success(request, resultado)
        return redirect('dashboard_users:resultados')


#---------------------------------
# INSCRIPCION
#---------------------------------

class InscripcionExamen(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/inscripcion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['examenes'] = Examen.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        examen_id = request.POST.get('examen_id')
        examen = get_object_or_404(Examen, id=examen_id)
        examen.usuarios.add(request.user)
        examen.save()
        messages.success(request, 'Te has inscrito exitosamente al examen.')
        return HttpResponseRedirect(reverse('dashboard_users:dashboard'))


#------------------------------
#   Resultados
#------------------------------

class ResultadosExamen(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/resultados.html'




