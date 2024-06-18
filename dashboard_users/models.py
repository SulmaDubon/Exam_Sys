from django.db import models
from users.models import CustomUser
from admin_panel.models import Examen

class InscripcionExamen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)

    def __str__(self):
        return f"Inscripción de {self.usuario} en {self.examen}"


