from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, CustomAuthenticationForm
from .models import CustomUser
import random
import string
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

@csrf_protect
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Hubo un error con el formulario. Por favor, revisa los datos ingresados.')
        return render(request, 'login.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
        return render(request, 'login.html', {'form': form})

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

def generate_username(first_name, last_name):
    base_username = f"{first_name.lower()}{last_name.lower()}"
    username = base_username
    counter = 1
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

class UserRegistrationView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = generate_username(user.first_name, user.last_name)
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.set_password(password)  # Esta línea encripta la contraseña
            try:
                user.save()
                # Enviar correo electrónico con las credenciales
                send_mail(
                    'Tus credenciales',
                    f'Nombre de usuario: {user.username}\nContraseña: {password}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Usuario creado exitosamente. Revisa tu correo electrónico para las credenciales.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
        else:
            messages.error(request, 'Hubo un error con el formulario. Por favor, revisa los datos ingresados.')
        return render(request, 'register.html', {'form': form})

class UserLoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            logger.debug(f"Intentando autenticar al usuario: {username}")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('dashboard')
            else:
                logger.warning(f"Autenticación fallida para el usuario: {username}")
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            logger.warning(f"Formulario no válido: {form.errors}")
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        return render(request, 'login.html', {'form': form})
