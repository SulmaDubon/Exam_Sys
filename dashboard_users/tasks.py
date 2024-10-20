from background_task import background
from django.utils import timezone
from .models import Examen, UserExam, InscripcionExamen
import random

@background(schedule=300)  # Tarea programada para ejecutarse 5 minutos antes del examen
def generar_examen_para_usuarios(examen_id):
    examen = Examen.objects.get(id=examen_id)
    inscripciones = InscripcionExamen.objects.filter(examen=examen)

    for inscripcion in inscripciones:
        usuario = inscripcion.usuario

        # Crear un nuevo UserExam para el usuario si no existe
        user_exam, created = UserExam.objects.get_or_create(usuario=usuario, examen=examen)

        if created:
            # Mezclar las preguntas y asignarlas al UserExam
            preguntas_seleccionadas = list(examen.preguntas.all())
            random.shuffle(preguntas_seleccionadas)

            # Asegurar que los enunciados y sus preguntas relacionadas se mantengan juntos
            preguntas_finales = []
            enunciados_vistos = set()

            for pregunta in preguntas_seleccionadas:
                if pregunta.enunciado:
                    # Si la pregunta es parte de un enunciado y no ha sido incluida
                    if pregunta.enunciado.id not in enunciados_vistos:
                        enunciados_vistos.add(pregunta.enunciado.id)
                        preguntas_finales.append(pregunta.enunciado)
                        preguntas_finales.extend(list(pregunta.enunciado.preguntas_relacionadas.all()))
                elif pregunta not in preguntas_finales:
                    preguntas_finales.append(pregunta)

            user_exam.preguntas.set(preguntas_finales)
            user_exam.save()

    print(f"Examen '{examen.nombre}' generado para todos los usuarios inscritos.")
