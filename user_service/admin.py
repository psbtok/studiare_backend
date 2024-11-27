from django.contrib import admin
from .models import Profile, Tutor

class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'about', 'birth_date', 'experienceYears')  # Поля для отображения в списке
    search_fields = ('about', 'education', 'links')  # Поля для поиска

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'is_tutor', 'get_tutor_info')  
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

    @admin.display(description="Имя")
    def get_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Фамилия")
    def get_last_name(self, obj):
        return obj.user.last_name

    @admin.display(description="Информация о репетиторе")
    def get_tutor_info(self, obj):
        return obj.tutor.about if obj.tutor else "Не указан"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Tutor, TutorAdmin)
