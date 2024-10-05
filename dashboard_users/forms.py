from django.utils import timezone
from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.forms import PasswordChangeForm
from .models import Examen, Pregunta, InscripcionExamen, Respuesta, TipoExamen, Modulo
from django.db.models import Q 

#--------------Formulario para crear o editar exámenes----------

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nombre', 'fecha', 'hora', 'tipo_examen', 'aprobacion_minima']
        labels = {
            'nombre': 'Nombre del examen',
            'fecha': 'Fecha del examen',
            'hora': 'Hora del examen',
            'tipo_examen': 'Tipo de examen',
            'aprobacion_minima': 'Nota mínima para aprobar'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'tipo_examen': forms.Select(attrs={'class': 'form-control'}),
            'aprobacion_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
        }


#---------------- Formulario para las respuestas asociadas a una pregunta

# Formulario para preguntas (con o sin enunciado)
class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['texto', 'modulo', 'enunciado']  # Incluye el campo enunciado opcional
        labels = {
            'texto': 'Texto de la pregunta o enunciado',
            'modulo': 'Módulo asociado',
            'enunciado': 'Enunciado (opcional)',
        }
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'modulo': forms.Select(attrs={'class': 'form-control'}),
            'enunciado': forms.Select(attrs={'class': 'form-control', 'empty_label': 'Sin enunciado'}),
        }

# Formulario para las preguntas derivadas (si el enunciado está presente)
class PreguntaDerivadaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['texto', 'activo']
        labels = {
            'texto': 'Texto de la pregunta derivada',
            'activo': '¿Está activa?',
        }
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formset para las preguntas derivadas de un enunciado
PreguntaDerivadaFormSet = inlineformset_factory(
    Pregunta,
    Pregunta,
    form=PreguntaDerivadaForm,
    fields=['texto', 'activo'],
    extra=3,  # Crear 3 preguntas derivadas
    max_num=3,
    can_delete=False,
)

# Formset para las respuestas de cada pregunta derivada
class RespuestaFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        correctas = 0
        for form in self.forms:
            if form.cleaned_data.get('es_correcta'):
                correctas += 1
        if correctas > 1:
            raise forms.ValidationError("Solo una respuesta puede ser marcada como correcta.")
        if correctas == 0:
            raise forms.ValidationError("Debe marcar al menos una respuesta como correcta.")

RespuestaFormSet = inlineformset_factory(
    Pregunta,
    Respuesta,
    form=forms.ModelForm,
    formset=RespuestaFormSet,
    fields=['texto', 'es_correcta'],
    extra=3,
    max_num=3,
    can_delete=False,
    widgets={
        'texto': forms.TextInput(attrs={'class': 'form-control'}),
        'es_correcta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)



# Formulario para subir un archivo Excel
class SubirPreguntasForm(forms.Form):
    archivo = forms.FileField(label='Archivo Excel', required=True)


# Formulario inscripcion de examen

class InscripcionExamenForm(forms.ModelForm):
    class Meta:
        model = InscripcionExamen
        fields = ['examen']  # Aquí incluimos el campo examen
        widgets = {
            'examen': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtener el usuario actual
        super().__init__(*args, **kwargs)

        # Filtrar los exámenes disponibles para el usuario
        self.fields['examen'].queryset = Examen.objects.filter(
            Q(fecha__gt=timezone.now().date()) | 
            (Q(fecha=timezone.now().date()) & Q(hora__gt=timezone.now().time()))
        ).exclude(inscripcionexamen__usuario=user)  # Excluir exámenes ya inscritos




# Formulario para cambiar contraseña
class CambiarContrasenaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(self.user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})



# Formulario para el TipoExamen
class TipoExamenForm(forms.ModelForm):
    class Meta:
        model = TipoExamen
        fields = ['nombre', 'tiempo_limite']
        labels = {
            'nombre': 'Nombre del tipo de examen',
            'tiempo_limite': 'Tiempo límite (minutos)'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tiempo_limite': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Formset para los Módulos
ModuloFormSet = inlineformset_factory(
    TipoExamen,  # Modelo padre
    Modulo,  # Modelo hijo
    form=forms.ModelForm,  # Formulario del modelo hijo
    fields=['nombre', 'cantidad_preguntas'],
    extra=1,  # Número de formularios adicionales a mostrar por defecto
    can_delete=True  # Permitir eliminar módulos del formset
)