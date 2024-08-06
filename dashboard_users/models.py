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

class Pregunta(models.Model):
    examen = models.ForeignKey(Examen, related_name='preguntas', on_delete=models.CASCADE, null=True, blank=True)
    texto = models.TextField()
    respuesta1 = models.CharField(max_length=255)
    respuesta2 = models.CharField(max_length=255)
    respuesta3 = models.CharField(max_length=255)
    respuesta4 = models.CharField(max_length=255)
    respuesta_correcta = models.CharField(max_length=1, choices=[('1', 'Respuesta 1'), ('2', 'Respuesta 2'), ('3', 'Respuesta 3'), ('4', 'Respuesta 4')])
    orden = models.IntegerField()

    def __str__(self):
        return self.texto

class ExclusionPregunta(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    excluida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pregunta} excluida de {self.examen}" if self.excluida else f"{self.pregunta} incluida en {self.examen}"
