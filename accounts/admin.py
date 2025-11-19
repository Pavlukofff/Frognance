from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# просмотр пользователей
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'date_joined')  # колонки в списке
    search_fields = ('username', 'email', 'phone')  # поиск по полям
    list_filter = ('is_staff', 'is_active', 'groups')  # фильтры по статусу
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'avatar')}),
    )
