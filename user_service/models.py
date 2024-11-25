from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Tutor(models.Model):
    about = models.TextField(blank=True, null=True, verbose_name='О себе')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    education = models.TextField(blank=True, null=True, verbose_name='Образование')
    links = models.TextField(blank=True, null=True, verbose_name='Ссылки')
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Возраст')

    class Meta:
        verbose_name = 'Репетитор'
        verbose_name_plural = 'Репетиторы'

    def __str__(self):
        return f"Репетитор {self.id} - {self.about[:50]}..." if self.about else f"Репетитор {self.id}"

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь"
    )
    is_tutor = models.BooleanField(
        default=False, 
        verbose_name="Репетитор",
    )
    tutor = models.OneToOneField(
        Tutor, 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
