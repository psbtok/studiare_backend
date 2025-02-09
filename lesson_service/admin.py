from django.contrib import admin
from .models import Lesson, Subject  # Import the Subject model

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
    search_fields = ('tutor__username', 'student__username', 'subject__title', 'notes')  # Updated to search by subject title

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

@admin.register(Subject) 
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'title', 
        'user', 
        'colorId'
    )
    list_filter = ('user',) 
    search_fields = ('title', 'user__username') 

    fieldsets = (
        (None, {
            'fields': (
                'title', 
                'user', 
                'notes', 
                'colorId'
            ),
            'description': 'Основная информация о предмете',
        }),
    )