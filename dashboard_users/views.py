from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def inscripcion(request):
    return render(request, 'inscripcion.html')

@login_required
def examen(request):
    return render(request, 'examen.html')

@login_required
def resultados(request):
    return render(request, 'resultados.html')

@login_required
def cambiar_contrasena(request):
    return render(request, 'cambiar_contrasena.html')
