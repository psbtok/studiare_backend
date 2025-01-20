from django.contrib import admin
from .models import Balance, Transaction

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # Показываем пользователя и его баланс в списке
    search_fields = ('user__username',)  # Поиск по имени пользователя
    list_filter = ('user',)  # Фильтрация по пользователю
    readonly_fields = ('user',)  # Поле пользователя только для чтения

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'type', 'date_created')  # Основные поля для отображения
    search_fields = ('sender__username', 'receiver__username')  # Поиск по имени отправителя и получателя
    list_filter = ('type', 'date_created')  # Фильтрация по типу и дате
    date_hierarchy = 'date_created'  # Удобная навигация по дате

# Регистрация моделей
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
