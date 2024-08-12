# dashboard_users/tasks.py
from celery import shared_task
from .models import CustomUser, Examen, Pregunta
import random

@shared_task
def generar_examen_async(usuario_id, examen_id):
    usuario = CustomUser.objects.get(id=usuario_id)
    examen = Examen.objects.get(id=examen_id)
    
    # Selección aleatoria de preguntas
    total_preguntas = Pregunta.objects.count()
    preguntas_a_mostrar = min(10, total_preguntas)  # Mostrar hasta 10 preguntas al azar
    preguntas = Pregunta.objects.order_by('?')[:preguntas_a_mostrar]

    # Aquí puedes realizar el procesamiento del examen, como guardar las preguntas seleccionadas, etc.
    # Ejemplo: Guardar preguntas seleccionadas en una tabla temporal
    for pregunta in preguntas:
        # Lógica para procesar cada pregunta
        pass

    return f"Examen generado para el usuario {usuario.username} en el examen {examen.nombre}"
