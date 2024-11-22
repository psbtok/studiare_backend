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
    )
    list_filter = ('isConfirmed', 'isCancelled', 'isConducted', 'date_start', 'subject')
    search_fields = ('tutor__username', 'student__username', 'subject', 'notes')
    ordering = ('-date_start',)
    readonly_fields = ('confirmationTime', 'cancellationTime')

    fieldsets = (
        (None, {
            'fields': (
                'tutor', 
                'student', 
                'subject', 
                'date_start', 
                'date_end', 
                'notes'
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
