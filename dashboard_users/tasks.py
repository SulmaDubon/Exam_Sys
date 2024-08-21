# dashboard_users/tasks.py
from celery import shared_task
from .models import Examen, UserExam, Pregunta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def preparar_examenes(examen_id):
    try:
        examen = Examen.objects.get(id=examen_id)
        usuarios = examen.usuarios.all()

        for usuario in usuarios:
            user_exam, created = UserExam.objects.get_or_create(usuario=usuario, examen=examen)

            if created:
                # Selección aleatoria de preguntas
                total_preguntas = Pregunta.objects.count()
                preguntas_a_mostrar = min(200, total_preguntas)
                preguntas = list(Pregunta.objects.order_by('?')[:preguntas_a_mostrar])
                user_exam.preguntas.set(preguntas)
            
            user_exam.inicio = timezone.now()
            user_exam.save()
    except Exception as e:
        logger.error(f"Error preparando examen {examen_id}: {str(e)}")
        raise e
