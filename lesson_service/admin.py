from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'tutor', 
        'student', 
        'subject', 
        'date_start', 
        'date_end',
        'isConfirmed', 
        'isCancelled', 
        'isConducted',
        'price'
    )
    list_filter = ('isConfirmed', 'isCancelled', 'isConducted', 'date_start', 'subject')
    search_fields = ('tutor__username', 'student__username', 'subject', 'notes')

    fieldsets = (
        (None, {
            'fields': (
                'tutor', 
                'student', 
                'subject', 
                'date_start', 
                'date_end', 
                'notes',
                'price'
            ),
            'description': 'Основная информация о занятии',
        }),
        ('Статусы', {
            'fields': (
                'isConfirmed', 
                'confirmationTime', 
                'isCancelled', 
                'cancellationTime', 
                'isConducted'
            ),
            'description': 'Информация о статусе занятия',
        }),
    )
