from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from users.models import CustomUser
from .models import Examen, Pregunta, InscripcionExamen
from django.core.exceptions import ValidationError

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



class CambiarContrasenaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(self.user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class SubirPreguntasForm(forms.Form):
    archivo = forms.FileField()