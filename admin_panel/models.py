#admin_panel/models.py

from django.db import models
from users.models import CustomUser

class Examen(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del examen")
    fecha = models.DateField()
    hora = models.TimeField()
    usuarios = models.ManyToManyField(CustomUser, through='dashboard_users.InscripcionExamen')

    def __str__(self):
        return f"Examen el {self.fecha} a las {self.hora}"
