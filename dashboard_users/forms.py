from django.utils import timezone
from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.forms import PasswordChangeForm
from .models import Examen, Pregunta, InscripcionExamen, Respuesta, TipoExamen, Modulo
from django.db.models import Q 
from django.db import models


# Clase base para los estilos de widgets
class BaseFormStyle:
    form_control = {'class': 'form-control'}

#--------------FORMULARIO PARA AGENDAR EXAMEN----------

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

# -------------------- FORMULARIO TIPO DE EXAMEN --------------------
# Formulario para el modelo TipoExamen
class TipoExamenForm(forms.ModelForm):
    class Meta:
        model = TipoExamen
        fields = ['nombre', 'tiempo_limite']
        labels = {
            'nombre': 'Nombre del tipo de examen',
            'tiempo_limite': 'Tiempo límite (minutos)'
        }
        widgets = {
            'nombre': forms.TextInput(attrs=BaseFormStyle.form_control),
            'tiempo_limite': forms.NumberInput(attrs=BaseFormStyle.form_control),
        }

    # Validación personalizada para asegurar que el tiempo límite sea positivo
    def clean_tiempo_limite(self):
        tiempo_limite = self.cleaned_data.get('tiempo_limite')
        if tiempo_limite <= 0:
            raise forms.ValidationError('El tiempo límite debe ser un número positivo.')
        return tiempo_limite

# -------------------- FORMULARIO MODULO --------------------
# Formulario para el modelo Modulo
class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ['nombre', 'cantidad_preguntas', 'tipo_examen']
        labels = {
            'nombre': 'Nombre del módulo',
            'cantidad_preguntas': 'Cantidad de preguntas'
        }
        widgets = {
            'nombre': forms.TextInput(attrs=BaseFormStyle.form_control),
            'cantidad_preguntas': forms.NumberInput(attrs=BaseFormStyle.form_control),
        }

# Formset para los Módulos usando el formulario personalizado
ModuloFormSet = inlineformset_factory(
    TipoExamen,  # Modelo padre
    Modulo,  # Modelo hijo
    form=ModuloForm,  # Formulario personalizado del modelo hijo
    fields=['nombre', 'cantidad_preguntas'],
    extra=1,  # Número de formularios adicionales a mostrar por defecto
    can_delete=True  # Habilitar la opción de eliminar formularios
)

# -------------------- FORMULARIO PREGUNTA --------------------

class PreguntaSimpleForm(forms.ModelForm):
    """Formulario para crear preguntas simples (independientes)."""

    class Meta:
        model = Pregunta
        fields = ['texto',  'tipo_examen', 'modulo']

    def clean(self):
        cleaned_data = super().clean()
        # Asegurarse de que no es una pregunta anidada
        if cleaned_data.get('enunciado'):
            raise forms.ValidationError("No puedes asignar un enunciado a una pregunta simple.")
        return cleaned_data


class PreguntaConEnunciadoForm(forms.ModelForm):
    """Formulario para crear un enunciado con tres preguntas relacionadas."""

    pregunta_1 = forms.CharField(label="Pregunta 1", widget=forms.Textarea)
    pregunta_2 = forms.CharField(label="Pregunta 2", widget=forms.Textarea)
    pregunta_3 = forms.CharField(label="Pregunta 3", widget=forms.Textarea)

    class Meta:
        model = Pregunta
        fields = ['texto', 'activo', 'tipo_examen', 'modulo']

    def clean(self):
        cleaned_data = super().clean()
        # Validar que el campo 'enunciado' no esté definido ya que esta es una pregunta principal
        if cleaned_data.get('enunciado'):
            raise forms.ValidationError("Esta es una pregunta enunciado, no puede tener un enunciado padre.")
        return cleaned_data

    def save(self, commit=True):
        # Crear el enunciado principal
        enunciado = super().save(commit=False)
        enunciado.save()

        # Crear las 3 preguntas anidadas relacionadas con este enunciado
        Pregunta.objects.create(
            texto=self.cleaned_data['pregunta_1'],
            activo=enunciado.activo,
            tipo_examen=enunciado.tipo_examen,
            modulo=enunciado.modulo,
            enunciado=enunciado
        )
        Pregunta.objects.create(
            texto=self.cleaned_data['pregunta_2'],
            activo=enunciado.activo,
            tipo_examen=enunciado.tipo_examen,
            modulo=enunciado.modulo,
            enunciado=enunciado
        )
        Pregunta.objects.create(
            texto=self.cleaned_data['pregunta_3'],
            activo=enunciado.activo,
            tipo_examen=enunciado.tipo_examen,
            modulo=enunciado.modulo,
            enunciado=enunciado
        )

        return enunciado

# Formulario para subir un archivo Excel
class SubirPreguntasForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo Excel',
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

# -------------------- FORMULARIO RESPUESTA --------------------

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['pregunta', 'texto', 'es_correcta', 'letra']
        labels = {
            'pregunta': 'Pregunta relacionada',
            'texto': 'Texto de la respuesta',
            'es_correcta': '¿Es la respuesta correcta?',
            'letra': 'Letra de la respuesta (opcional)'
        }
        widgets = {
            'pregunta': forms.Select(attrs=BaseFormStyle.form_control),
            'texto': forms.TextInput(attrs=BaseFormStyle.form_control),
            'es_correcta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'letra': forms.Select(attrs=BaseFormStyle.form_control),
        }

    def clean(self):
        cleaned_data = super().clean()
        pregunta = cleaned_data.get('pregunta')
        es_correcta = cleaned_data.get('es_correcta')

        # Validar que no haya más de tres respuestas para la misma pregunta
        numero_respuestas = Respuesta.objects.filter(pregunta=pregunta).exclude(pk=self.instance.pk).count()
        if self.instance.pk is None and numero_respuestas >= 3:
            raise forms.ValidationError("No se pueden agregar más de tres respuestas a una pregunta.")

        # Asegurarse de que solo una respuesta sea marcada como correcta
        if es_correcta:
            if Respuesta.objects.filter(pregunta=pregunta, es_correcta=True).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Solo una respuesta puede ser la correcta para cada pregunta.")

        return cleaned_data

    def save(self, *args, **kwargs):
        # Asignar letra automáticamente si no está asignada
        if not self.instance.letra:  # Usar self.instance en lugar de cleaned_data
            numero_respuestas = Respuesta.objects.filter(pregunta=self.instance.pregunta).exclude(pk=self.instance.pk).count()
            self.instance.letra = ['A', 'B', 'C'][numero_respuestas]
        return super().save(*args, **kwargs)


# Inline formset para manejar las respuestas relacionadas a una pregunta
RespuestaFormSet = inlineformset_factory(
    Pregunta,
    Respuesta,
    form=RespuestaForm,
    extra=3,  # Número de formularios adicionales
    can_delete=True  # Permitir eliminar respuestas
)
 
#-----------------INSCRIPCION-----------------------------

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

#-----------------CAMBIAR CONTRASEÑA-----------------------------
# Formulario para cambiar contraseña
class CambiarContrasenaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(self.user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})






