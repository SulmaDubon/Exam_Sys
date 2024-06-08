from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from dashboard_users.models import Examen, UserExam
from users.models import CustomUser
from .forms import FormularioUsuario, FormularioExamen

def es_admin(usuario):
    return usuario.is_superuser

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class VistaAdminPanel(View):
    def get(self, request):
        return render(request, 'admin_panel/admin_panel.html')

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaUsuarios(View):
    def get(self, request):
        usuarios = CustomUser.objects.all()
        return render(request, 'admin_panel/lista_usuarios.html', {'usuarios': usuarios})

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaExamenes(View):
    def get(self, request):
        examenes = Examen.objects.all()
        return render(request, 'admin_panel/lista_examenes.html', {'examenes': examenes})

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarUsuario(View):
    def get(self, request, usuario_id):
        usuario = get_object_or_404(CustomUser, id=usuario_id)
        formulario = FormularioUsuario(instance=usuario)
        return render(request, 'admin_panel/formulario_usuario.html', {'formulario': formulario, 'usuario': usuario})

    def post(self, request, usuario_id):
        usuario = get_object_or_404(CustomUser, id=usuario_id)
        formulario = FormularioUsuario(request.POST, instance=usuario)
        if formulario.is_valid():
            formulario.save()
            return redirect('admin_panel:lista_usuarios')
        return render(request, 'admin_panel/formulario_usuario.html', {'formulario': formulario, 'usuario': usuario})

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class EditarExamen(View):
    def get(self, request, examen_id):
        examen = get_object_or_404(Examen, id=examen_id)
        formulario = FormularioExamen(instance=examen)
        return render(request, 'admin_panel/formulario_examen.html', {'formulario': formulario, 'examen': examen})

    def post(self, request, examen_id):
        examen = get_object_or_404(Examen, id=examen_id)
        formulario = FormularioExamen(request.POST, instance=examen)
        if formulario.is_valid():
            formulario.save()
            return redirect('admin_panel:lista_examenes')
        return render(request, 'admin_panel/formulario_examen.html', {'formulario': formulario, 'examen': examen})

@method_decorator([login_required, user_passes_test(es_admin)], name='dispatch')
class ListaResultados(View):
    def get(self, request):
        resultados = UserExam.objects.all()
        return render(request, 'admin_panel/lista_resultados.html', {'resultados': resultados})
