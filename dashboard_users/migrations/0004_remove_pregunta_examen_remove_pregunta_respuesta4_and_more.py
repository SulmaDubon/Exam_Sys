# Generated by Django 5.0.6 on 2024-09-11 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_users', '0003_remove_pregunta_campo_temporal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pregunta',
            name='examen',
        ),
        migrations.RemoveField(
            model_name='pregunta',
            name='respuesta4',
        ),
        migrations.AlterField(
            model_name='pregunta',
            name='respuesta_correcta',
            field=models.CharField(choices=[('1', 'Respuesta 1'), ('2', 'Respuesta 2'), ('3', 'Respuesta 3')], max_length=1),
        ),
    ]
