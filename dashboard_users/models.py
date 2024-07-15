# dashboard_users/models.py
from django.db import models
from django.utils import timezone
from users.models import CustomUser



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

#----------------------------------------
#       PREGUNTAS
#----------------------------------------

class Pregunta(models.Model):
    texto = models.TextField(verbose_name="Texto de la pregunta")
    respuesta_correcta = models.CharField(max_length=255, verbose_name="Respuesta correcta")
    respuesta1 = models.CharField(max_length=255, verbose_name="Respuesta 1")
    respuesta2 = models.CharField(max_length=255, verbose_name="Respuesta 2")
    respuesta3 = models.CharField(max_length=255, verbose_name="Respuesta 3")
    respuesta4 = models.CharField(max_length=255, verbose_name="Respuesta 4")

    def __str__(self):
        return self.texto


class ExclusionPregunta(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    excluida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pregunta} excluida de {self.examen}" if self.excluida else f"{self.pregunta} incluida en {self.examen}"