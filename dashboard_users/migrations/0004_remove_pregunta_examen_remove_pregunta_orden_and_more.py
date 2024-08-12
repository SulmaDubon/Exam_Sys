# Generated by Django 5.0.6 on 2024-08-06 18:03

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
            name='orden',
        ),
        migrations.AlterField(
            model_name='pregunta',
            name='respuesta_correcta',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='pregunta',
            name='texto',
            field=models.CharField(max_length=255),
        ),
    ]
