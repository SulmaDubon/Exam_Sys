# dashboard_users/models.py
from django.db import models
from django.utils import timezone
from users.models import CustomUser
from django.contrib.auth import get_user_model


class Examen(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del examen")
    fecha = models.DateField()
    hora = models.TimeField()
    usuarios = models.ManyToManyField(CustomUser, through='InscripcionExamen')

    def __str__(self):
        return f"Examen el {self.fecha} a las {self.hora}"
    

class InscripcionExamen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    resultado = models.CharField(max_length=100, blank=True, null=True)
    fecha_inscripcion = models.DateField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Inscripción de {self.usuario.username} en {self.examen.nombre}"


class Pregunta(models.Model):
    texto = models.TextField()
    respuesta1 = models.CharField(max_length=255)
    respuesta2 = models.CharField(max_length=255)
    respuesta3 = models.CharField(max_length=255)
    respuesta_correcta = models.CharField(max_length=1, choices=[
        ('1', 'Respuesta 1'),
        ('2', 'Respuesta 2'),
        ('3', 'Respuesta 3')])
    orden = models.IntegerField()

    def __str__(self):
        return self.texto



class UserExam(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey('Examen', on_delete=models.CASCADE)
    preguntas = models.ManyToManyField('Pregunta')
    inicio = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    respuestas = models.JSONField(default=dict)  # Guardar las respuestas del examen

    def tiempo_restante(self):
        """Calcula el tiempo restante en formato de horas y minutos."""
        tiempo_maximo = 3 * 60 * 60  # 3 horas en segundos
        tiempo_transcurrido = (timezone.now() - self.inicio).total_seconds()
        tiempo_restante = max(0, tiempo_maximo - tiempo_transcurrido)
        horas_restantes = int(tiempo_restante // 3600)
        minutos_restantes = int((tiempo_restante % 3600) // 60)
        return f"{horas_restantes:02}:{minutos_restantes:02}"

    def examen_finalizado(self):
        """Marca el examen como finalizado."""
        self.finalizado = True
        self.fecha_envio = timezone.now()
        self.save()

    

class ExclusionPregunta(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    excluida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pregunta} excluida de {self.examen}" if self.excluida else f"{self.pregunta} incluida en {self.examen}"
