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
    respuesta_correcta = forms.ChoiceField(
        choices=[('1', 'Respuesta 1'), ('2', 'Respuesta 2'), ('3', 'Respuesta 3')],
        widget=forms.RadioSelect,
        label='Marque la correcta'
    )

    class Meta:
        model = Pregunta
        fields = ['texto', 'respuesta1', 'respuesta2', 'respuesta3', 'respuesta_correcta', 'orden']
        labels = {
            'texto': 'Texto de la Pregunta',
            'respuesta1': 'Respuesta 1',
            'respuesta2': 'Respuesta 2',
            'respuesta3': 'Respuesta 3',
            'orden': 'Orden de visualización'
        }

    def clean(self):
        cleaned_data = super().clean()
        respuesta_correcta = cleaned_data.get('respuesta_correcta')

        if not respuesta_correcta:
            self.add_error('respuesta_correcta', 'Debe seleccionar la respuesta correcta.')

        return cleaned_data
    

class SubirPreguntasForm(forms.Form):
    archivo = forms.FileField(label='Archivo Excel', required=True)







class CambiarContrasenaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(self.user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
