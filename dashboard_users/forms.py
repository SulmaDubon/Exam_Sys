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

class PreguntaForm(forms.ModelForm):
    es_enunciado = forms.BooleanField(
        label='¿Es un enunciado?', 
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_es_enunciado'})
    )
    
    class Meta:
        model = Pregunta
        fields = ['texto', 'tipo_examen', 'modulo', 'enunciado']
        labels = {
            'texto': 'Texto de la pregunta o enunciado',
            'tipo_examen': 'Tipo de Examen',
            'modulo': 'Módulo asociado',
            'enunciado': 'Enunciado (opcional)',
        }
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_examen': forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo_examen'}),
            'modulo': forms.Select(attrs={'class': 'form-control', 'id': 'id_modulo'}),
            'enunciado': forms.Select(attrs={'class': 'form-control', 'empty_label': 'Sin enunciado'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['modulo'].queryset = Modulo.objects.none()

        if 'tipo_examen' in self.data:
            try:
                tipo_examen_id = int(self.data.get('tipo_examen'))
                self.fields['modulo'].queryset = Modulo.objects.filter(tipo_examen_id=tipo_examen_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['modulo'].queryset = self.instance.tipo_examen.modulo_set.all()



# Formulario para respuestas asociadas a una pregunta
class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['texto', 'es_correcta']
        labels = {
            'texto': 'Texto de la respuesta',
            'es_correcta': '¿Es la respuesta correcta?',
        }
        widgets = {
            'texto': forms.TextInput(attrs={'class': 'form-control'}),
            'es_correcta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formset para las respuestas
RespuestaFormSet = inlineformset_factory(
    Pregunta,
    Respuesta,
    form=RespuestaForm,
    extra=3,
    max_num=3,
    can_delete=False,
)



# Formulario para subir un archivo Excel
class SubirPreguntasForm(forms.Form):
    archivo = forms.FileField(label='Archivo Excel', required=True)


#----------------------------------------------
#                INSCRIPCION
#------------------------------------------------

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



# Clase base para los estilos de widgets
class BaseFormStyle:
    form_control = {'class': 'form-control'}

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

# Formulario para el modelo Modulo
class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ['nombre', 'cantidad_preguntas']
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