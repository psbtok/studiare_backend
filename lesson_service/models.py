from django.db import models
from django.conf import settings

class Lesson(models.Model):
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='lessons_as_tutor', 
        verbose_name='Репетитор',
        null=True,
        blank=True  
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='lessons_as_student', 
        verbose_name='Ученик'
    )
    subject = models.CharField(max_length=100, verbose_name='Предмет')
    date_start = models.DateTimeField(blank=True, null=True, verbose_name='Время начала занятия')
    date_end = models.DateTimeField(blank=True, null=True, verbose_name='Время конца занятия')
    notes = models.TextField(blank=True, null=True, verbose_name='Заметки')
    price = models.IntegerField(blank=True, null=True)
    
    isConfirmed = models.BooleanField(blank=True, null=True, verbose_name='Подтверждено')
    confirmationTime = models.DateTimeField(blank=True, null=True, verbose_name='Время подтверждения')
    
    isCancelled = models.BooleanField(blank=True, null=True, verbose_name='Отменено')
    cancellationTime = models.DateTimeField(blank=True, null=True, verbose_name='Время отмены')

    isConducted = models.BooleanField(blank=True, null=True, verbose_name='Проведено')

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['-date_start']

    def __str__(self):
        if self.date_start:
            return f"{self.subject} ({self.date_start.strftime('%Y-%m-%d %H:%M')})"
        return f"{self.subject} (Дата не указана)"
