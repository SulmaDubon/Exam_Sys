# dashboard_users/models.py
from django.db import models
from django.utils import timezone
from users.models import CustomUser
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils.timezone import make_aware

User = get_user_model()

class Examen(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del examen")
    fecha = models.DateField()
    hora = models.TimeField()
    usuarios = models.ManyToManyField(CustomUser, through='InscripcionExamen')

    def __str__(self):
        return f"Examen el {self.fecha} a las {self.hora}"

    @property
    def fecha_hora_inicio(self):
        # Combina la fecha y la hora en un solo objeto datetime
        # Este datetime será "naive", es decir, no contendrá información de zona horaria
        return datetime.combine(self.fecha, self.hora)
    

class InscripcionExamen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    resultado = models.CharField(max_length=100, blank=True, null=True)
    fecha_inscripcion = models.DateField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Inscripción de {self.usuario.username} en {self.examen.nombre}"

class Pregunta(models.Model):
    texto = models.CharField(max_length=255)  # Corrección: max_length en lugar de maxlength
    respuesta_correcta = models.CharField(max_length=255)  # Corrección: max_length en lugar de maxlength
    respuesta1 = models.CharField(max_length=255)  # Corrección: max_length en lugar de maxlength
    respuesta2 = models.CharField(max_length=255)  # Corrección: max_length en lugar de maxlength
    respuesta3 = models.CharField(max_length=255)  # Corrección: max_length en lugar de maxlength
    respuesta4 = models.CharField(max_length=255)  # Corrección: max_length en lugar de maxlength

    def __str__(self):
        return self.texto



class UserExam(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    preguntas = models.ManyToManyField(Pregunta)
    inicio = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)
   
    def __str__(self):
        return f"{self.usuario.username} - {self.examen.nombre}"