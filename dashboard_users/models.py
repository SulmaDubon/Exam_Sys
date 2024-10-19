# dashboard_users/models.py
from django.db import models
from django.utils import timezone
from users.models import CustomUser

# Función para devolver la hora por defecto del examen
def default_exam_time():
    return timezone.now().time()


# --------------- CONFIGURACION TIPO DE EXAMEN---------------
class TipoExamen(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    tiempo_limite = models.PositiveIntegerField(help_text="Tiempo límite en minutos")
    
    def total_preguntas(self):
        """Devuelve la suma total de preguntas de todos los módulos asociados a este tipo de examen."""
        return sum(modulo.cantidad_preguntas for modulo in self.modulos.all())

    def __str__(self):
        return self.nombre

class Modulo(models.Model):
    nombre = models.CharField(max_length=255)
    cantidad_preguntas = models.PositiveIntegerField()
    tipo_examen = models.ForeignKey(TipoExamen, on_delete=models.CASCADE, related_name='modulos')

    def __str__(self):
        return f"{self.nombre} - {self.cantidad_preguntas} preguntas"


#------------------- PREGUNTA ----------------------------------------

class Pregunta(models.Model):
    texto = models.TextField()  # El texto de la pregunta o enunciado
    activo = models.BooleanField(default=True)
    tipo_examen = models.ForeignKey(TipoExamen, on_delete=models.CASCADE, related_name='preguntas')  # Asociación directa al tipo de examen
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='preguntas')  # Asociar a módulo
    enunciado = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='preguntas_relacionadas'
    )  # Relación para preguntas anidadas

    def es_enunciado(self):
        """Determina si la pregunta es un enunciado (sin estar relacionada a otro enunciado)."""
        return self.enunciado is None

    def save(self, *args, **kwargs):
        if self.enunciado:
            # Verificar que no existan más de 3 preguntas anidadas para un enunciado
            if self.enunciado.preguntas_relacionadas.count() >= 3:
                raise ValueError("Cada enunciado puede tener un máximo de 3 preguntas anidadas.")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.es_enunciado():
            return f"Enunciado: {self.texto} (Módulo: {self.modulo.nombre}, Tipo de Examen: {self.tipo_examen.nombre})"
        else:
            return f"Pregunta: {self.texto} (Módulo: {self.modulo.nombre}, Tipo de Examen: {self.tipo_examen.nombre})"

#----------------------- RESPUESTAS ----------------------------

class Respuesta(models.Model):
    LETRA_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='respuestas')
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    letra = models.CharField(max_length=1, choices=LETRA_CHOICES, blank=True)

    def save(self, *args, **kwargs):
        # Validar que no haya más de tres respuestas para la misma pregunta
        numero_respuestas = Respuesta.objects.filter(pregunta=self.pregunta).count()
        if numero_respuestas >= 3:
            raise ValueError("No se pueden agregar más de tres respuestas a una pregunta.")

        # Asignar letra automáticamente si no está asignada
        if not self.letra:
            self.letra = ['A', 'B', 'C'][numero_respuestas]

        # Asegurarse de que solo una respuesta sea marcada como correcta
        if self.es_correcta:
            if Respuesta.objects.filter(pregunta=self.pregunta, es_correcta=True).exists():
                raise ValueError("Solo una respuesta puede ser la correcta para cada pregunta.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Respuesta {self.letra}: {self.texto} (Correcta: {self.es_correcta})"

#-------------------- AGENDA EXAMEN --------------------------------

class Examen(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre del examen")
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=default_exam_time)
    usuarios = models.ManyToManyField(CustomUser, through='InscripcionExamen')
    tipo_examen = models.ForeignKey(TipoExamen, on_delete=models.CASCADE, related_name='examenes')  # Relación con TipoExamen
    aprobacion_minima = models.FloatField(default=6.0, verbose_name="Nota mínima para aprobar")

    def obtener_tiempo_limite(self):
        """Devuelve el tiempo límite del examen en formato HH:MM basado en el tipo de examen."""
        tiempo_limite = self.tipo_examen.tiempo_limite  # Tiempo límite en minutos desde TipoExamen
        horas = tiempo_limite // 60
        minutos = tiempo_limite % 60
        return f"{horas:02}:{minutos:02}"

    def __str__(self):
        return f"{self.tipo_examen.nombre}: Examen el {self.fecha} a las {self.hora}"






#----------------------- INSCRIPCION ----------------------------------

class InscripcionExamen(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    resultado = models.CharField(max_length=100, blank=True, null=True)
    fecha_inscripcion = models.DateField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Inscripción de {self.usuario.username} en {self.examen.nombre}"

#------------------- USEREXAM -----------------------------------------
class UserExam(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    preguntas = models.ManyToManyField(Pregunta)
    inicio = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    respuestas = models.JSONField(default=dict)
    nota = models.FloatField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=[('Aprobado', 'Aprobado'), ('Reprobado', 'Reprobado')], null=True, blank=True)

    def tiempo_restante(self):
        """Calcula el tiempo restante en horas y minutos usando la zona horaria correcta."""
        tiempo_maximo = self.examen.tipo_examen.tiempo_limite * 60  # Convertir a segundos
        tiempo_transcurrido = (timezone.now() - self.inicio).total_seconds()
        tiempo_restante = max(0, tiempo_maximo - tiempo_transcurrido)
        horas_restantes = tiempo_restante // 3600
        minutos_restantes = (tiempo_restante % 3600) // 60
        return f"{int(horas_restantes):02}:{int(minutos_restantes):02}"

    def examen_finalizado(self):
        """Marca el examen como finalizado."""
        if not self.finalizado:
            self.finalizado = True
            self.fecha_envio = timezone.now()
            self.save()

    def calcular_nota(self):
        """Calcula y asigna la nota del examen basado en las respuestas correctas de forma más eficiente."""
        total_preguntas = self.preguntas.count()
        if total_preguntas > 0:
            preguntas = self.preguntas.prefetch_related('respuestas')
            respuestas_correctas = 0

            # Comprobar respuestas correctas de manera más eficiente
            for pregunta in preguntas:
                respuesta_usuario = self.respuestas.get(str(pregunta.id), None)
                if respuesta_usuario and pregunta.respuestas.filter(es_correcta=True, texto=respuesta_usuario).exists():
                    respuestas_correctas += 1

            # Calcular la nota en porcentaje
            self.nota = (respuestas_correctas / total_preguntas) * 100
        else:
            self.nota = 0
        self.save()
        self.actualizar_estado()



