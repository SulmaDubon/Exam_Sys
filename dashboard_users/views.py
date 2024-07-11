# dashboard_users/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from .models import Examen
from .forms import ExamenForm

from .forms import CambiarContrasenaForm

class VistaDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/dashboard.html'

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
            # Redirigir a alguna página de éxito o mostrar un mensaje
            return redirect('dashboard_users:dashboard')
        return render(request, self.template_name, {'form': form})

class VistaExamen(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/examen.html'

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
        return HttpResponseRedirect(reverse('dashboard_users:inscripcion_exitosa'))



class ResultadosExamen(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard_users/resultados.html'
