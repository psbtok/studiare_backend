# Generated by Django 5.1.2 on 2025-02-15 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_service', '0004_remove_tutor_age_tutor_experienceyears'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/', verbose_name='Фото профиля'),
        ),
    ]
