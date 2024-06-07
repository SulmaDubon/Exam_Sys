from rest_framework import viewsets
from django.shortcuts import render
from .models import Pregunta, Examen, ResultadoExamen
from .serializers import PreguntaSerializer, ExamenSerializer, ResultadoExamenSerializer

class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer

class ExamenViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer

class ResultadoExamenViewSet(viewsets.ModelViewSet):
    queryset = ResultadoExamen.objects.all()
    serializer_class = ResultadoExamenSerializer

# Añadir vista index
def index(request):
    return render(request, 'index.html')
