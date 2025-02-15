from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Tutor

class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'about', 'birth_date', 'experienceYears')  # Поля для отображения в списке
    search_fields = ('about', 'education', 'links', 'paymentMethod')  # Поля для поиска

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'is_tutor', 'get_tutor_info', 'display_profile_picture')  
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('display_profile_picture',)  # Make the profile picture read-only in the detail view

    @admin.display(description="Имя")
    def get_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Фамилия")
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(description="Информация о репетиторе")
    def get_tutor_info(self, obj):
        return obj.tutor.about if obj.tutor else "Не указан"

    @admin.display(description="Фото профиля")
    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return "Нет фото"

    # Customize the fields displayed in the detail view
    fieldsets = (
        (None, {
            'fields': ('user', 'is_tutor', 'tutor', 'profile_picture', 'display_profile_picture')
        }),
    )

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Tutor, TutorAdmin)