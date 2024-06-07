from django.urls import path
from .views import UserRegistrationView, UserLoginView, home, dashboard, inscripcion, examen, resultados, cambiar_contrasena

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('inscripcion/', inscripcion, name='inscripcion'),
    path('examen/', examen, name='examen'),
    path('resultados/', resultados, name='resultados'),
    path('cambiar_contrasena/', cambiar_contrasena, name='cambiar_contrasena'),
]





