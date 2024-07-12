# dashboard_users/models.py
from django.db import models
from users.models import CustomUser



class Examen(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del examen")
    fecha = models.DateField()
    hora = models.TimeField()
    usuarios = models.ManyToManyField(CustomUser, through='dashboard_users.InscripcionExamen')

    def __str__(self):
        return f"Examen el {self.fecha} a las {self.hora}"


class InscripcionExamen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Inscripción de {self.usuario.username} en {self.examen.nombre}"
