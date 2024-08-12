# Generated by Django 5.0.6 on 2024-08-07 17:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_users', '0004_remove_pregunta_examen_remove_pregunta_orden_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField(auto_now_add=True)),
                ('finalizado', models.BooleanField(default=False)),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard_users.examen')),
                ('preguntas', models.ManyToManyField(to='dashboard_users.pregunta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='ExclusionPregunta',
        ),
    ]
