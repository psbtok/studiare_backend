from django.db import models
from django.conf import settings

class LessonParticipant(models.Model):
    class Status(models.TextChoices):
        AWAITING_CONFIRMATION = 'awaiting_confirmation', 'Awaiting Confirmation'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        CONDUCTED = 'conducted', 'Conducted'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_participants',
        verbose_name='Участник'
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Занятие'
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.AWAITING_CONFIRMATION,
        verbose_name='Статус'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления статуса')

    class Meta:
        unique_together = ('user', 'lesson')  
        verbose_name = 'Участник занятия'
        verbose_name_plural = 'Участники занятий'

    def __str__(self):
        return f"{self.user} - {self.lesson} ({self.status})"

class Subject(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название предмета')
    notes = models.TextField(blank=True, null=True, verbose_name='Заметки')
    colorId = models.IntegerField(blank=True, null=True, verbose_name='ID цвета')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'
        ordering = ['title']

    def __str__(self):
        return self.title

class Lesson(models.Model):
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='lessons_as_tutor', 
        verbose_name='Репетитор',
        null=True,
        blank=True  
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Предмет'
    )
    date_start = models.DateTimeField(blank=True, null=True, verbose_name='Время начала занятия')
    date_end = models.DateTimeField(blank=True, null=True, verbose_name='Время конца занятия')
    notes = models.TextField(blank=True, null=True, verbose_name='Заметки')
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.date_start:
            return f"{self.subject.title} ({self.date_start.strftime('%Y-%m-%d %H:%M')})"
        return f"{self.subject.title} (Дата не указана)"