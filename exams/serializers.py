from rest_framework import serializers
from .models import Pregunta, Examen, ResultadoExamen

class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pregunta
        fields = '__all__'

class ExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = '__all__'

class ResultadoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoExamen
        fields = '__all__'
