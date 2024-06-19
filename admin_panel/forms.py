# admin_panel/forms.py

from django import forms
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
