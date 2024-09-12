#!/bin/bash

# Salir si hay algún error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones de la base de datos
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Cualquier otra configuración o comandos necesarios para tu aplicación
