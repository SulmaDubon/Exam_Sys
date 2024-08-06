# dashboard_users/tasks.py
from celery import shared_task

@shared_task
def generar_examen(usuario_id, examen_id):
    from .models import CustomUser, Examen, Pregunta, InscripcionExamen
    import random

    usuario = CustomUser.objects.get(id=usuario_id)
    examen = Examen.objects.get(id=examen_id)
    preguntas = Pregunta.objects.filter(examen=examen).order_by('?')[:10]  # 10 preguntas aleatorias

    inscripcion, created = InscripcionExamen.objects.get_or_create(usuario=usuario, examen=examen)

    # Aquí puedes realizar el procesamiento del examen, como guardar respuestas, etc.
    return f"Examen generado para el usuario {usuario.username} en el examen {examen.nombre}"
