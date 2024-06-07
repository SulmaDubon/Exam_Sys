from django.db import models
from users.models import CustomUser

class Pregunta(models.Model):
    texto = models.TextField()
    opcion1 = models.CharField(max_length=200)
    opcion2 = models.CharField(max_length=200)
    opcion3 = models.CharField(max_length=200)
    opcion4 = models.CharField(max_length=200)
    opcion5 = models.CharField(max_length=200)
    opcion_correcta = models.CharField(max_length=200)

    def __str__(self):
        return self.texto

class Examen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha_programada = models.DateTimeField()
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"Examen para {self.usuario.email} el {self.fecha_programada}"

class ResultadoExamen(models.Model):
    examen = models.OneToOneField(Examen, on_delete=models.CASCADE)
    puntaje = models.FloatField()
    aprobado = models.BooleanField()

    def __str__(self):
        return f"Resultado para {self.examen.usuario.email}: {self.puntaje}"
