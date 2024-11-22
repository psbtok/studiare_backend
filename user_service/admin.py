from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'is_tutor')  
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

    @admin.display(description="Имя")
    def get_first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Фамилия")
    def get_last_name(self, obj):
        return obj.user.last_name

admin.site.register(Profile, ProfileAdmin)
