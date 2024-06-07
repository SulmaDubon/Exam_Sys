from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreguntaViewSet, ExamenViewSet, ResultadoExamenViewSet, index

router = DefaultRouter()
router.register(r'preguntas', PreguntaViewSet)
router.register(r'examenes', ExamenViewSet)
router.register(r'resultados', ResultadoExamenViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('', include(router.urls)),
]
