from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, CustomAuthenticationForm
from .models import CustomUser
import random
import string
import logging

# Configurar el logger
logger = logging.getLogger(__name__)

def generate_username(first_name, last_name):
    base_username = f"{first_name.lower()}{last_name.lower()}"
    username = base_username
    counter = 1
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username

def generate_password(length=8):
    """Genera una contraseña aleatoria."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class UserRegistrationView(ListView):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'user/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = generate_username(user.first_name, user.last_name)
            password = generate_password()
            user.set_password(password)
            try:
                user.save()
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
                logger.error(f'Error al crear el usuario: {str(e)}')
                messages.error(request, 'Error al crear el usuario. Por favor, inténtelo de nuevo.')
        else:
            messages.error(request, 'Hubo un error con el formulario. Por favor, revisa los datos ingresados.')
            logger.warning(f"Formulario de registro no válido: {form.errors}")
        return render(request, 'user/register.html', {'form': form})

@method_decorator(csrf_protect, name='dispatch')
class UserLoginView(ListView):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, 'user/login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            logger.debug(f"Intentando autenticar al usuario: {username}")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('dashboard_users:dashboard')
            else:
                logger.warning(f"Autenticación fallida para el usuario: {username}")
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            logger.warning(f"Formulario no válido: {form.errors}")
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        return render(request, 'user/login.html', {'form': form})
