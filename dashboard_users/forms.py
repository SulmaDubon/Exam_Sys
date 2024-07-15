from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from users.models import CustomUser
from .models import Examen, Pregunta, InscripcionExamen


class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nombre', 'fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'nombre': 'Nombre del Examen',
            'fecha': 'Fecha del Examen',
            'hora': 'Hora del Examen',
            
        }


class ResultadoForm(forms.ModelForm):
    class Meta:
        model = InscripcionExamen
        fields = ['resultado']
        labels = {
            'resultado': 'Resultado del Examen'
        }
        

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['texto', 'respuesta_correcta', 'respuesta1', 'respuesta2', 'respuesta3', 'respuesta4']
        labels = {
            'texto': 'Texto de la Pregunta',
            'respuesta_correcta': 'Respuesta Correcta',
            'respuesta1': 'Respuesta 1',
            'respuesta2': 'Respuesta 2',
            'respuesta3': 'Respuesta 3',
            'respuesta4': 'Respuesta 4'
        }






class CambiarContrasenaForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
