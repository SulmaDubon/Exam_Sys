# dashboard_users/models.py
from django.db import models
from users.models import CustomUser
from admin_panel.models import Examen

class InscripcionExamen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    resultado = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Inscripción de {self.usuario.username} en {self.examen.nombre}"
