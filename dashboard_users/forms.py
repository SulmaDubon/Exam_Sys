from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from users.models import CustomUser
from .models import Examen

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nombre', 'fecha', 'hora', 'usuarios']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'nombre': 'Nombre del Examen',
            'fecha': 'Fecha del Examen',
            'hora': 'Hora del Examen',
            'usuarios': 'Usuarios Inscritos'
        }


class CambiarContrasenaForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
