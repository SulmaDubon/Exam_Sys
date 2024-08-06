# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establece el módulo de configuración predeterminado de Django para 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Usa una cadena aquí para que el trabajador de Celery no tenga que serializar
# la configuración de configuración de Django a un archivo
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carga tareas de todos los módulos de tareas en todos los paquetes de aplicaciones Django
app.autodiscover_tasks()
