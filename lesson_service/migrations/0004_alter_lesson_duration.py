# Generated by Django 5.1.2 on 2024-11-22 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson_service', '0003_alter_lesson_tutor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='duration',
            field=models.IntegerField(verbose_name='Длительность'),
        ),
    ]
