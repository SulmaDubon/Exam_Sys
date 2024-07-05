# Generated by Django 5.0.6 on 2024-07-05 10:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admin_panel', '0001_initial'),
        ('dashboard_users', '0003_remove_question_choices_remove_exam_questions_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='examen',
            name='usuarios',
            field=models.ManyToManyField(through='dashboard_users.InscripcionExamen', to=settings.AUTH_USER_MODEL),
        ),
    ]
