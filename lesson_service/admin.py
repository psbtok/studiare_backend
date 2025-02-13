from django.contrib import admin
from .models import Lesson, Subject, LessonParticipant  # Import the LessonParticipant model

class LessonParticipantInline(admin.TabularInline):
    model = LessonParticipant
    extra = 1  # Number of empty forms to display


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'tutor', 
        'subject', 
        'date_start', 
        'date_end',
        'price',
    )
    list_filter = ('date_start', 'subject')
    search_fields = ('tutor__username', 'subject__title', 'notes')

    fieldsets = (
        (None, {
            'fields': (
                'tutor', 
                'subject',
                'date_start', 
                'date_end', 
                'notes',
                'price'
            ),
            'description': 'Основная информация о занятии',
        }),
    )

    # Inline for LessonParticipant
    inlines = [LessonParticipantInline]

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

# Ensure the LessonParticipant model is registered
@admin.register(LessonParticipant)
class LessonParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'lesson__subject__title')

    fieldsets = (
        (None, {
            'fields': (
                'user', 
                'lesson', 
                'status', 
            ),
            'description': 'Основная информация об участнике занятия',
        }),
    )

