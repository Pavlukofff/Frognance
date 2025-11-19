from django.contrib import admin
from .models import Category, Transaction, UserGroup, UserGroupMember


# Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'group', 'is_income', 'icon')  # колонки в списке
    search_fields = ('name',)  # поиск по имени
    list_filter = ('is_income', 'user')  # фильтры тип, пользователь


# Transaction
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('t_type', 'amount', 'user', 'group', 'category', 'date')  # колонки
    search_fields = ('description',)  # поиск по описанию
    list_filter = ('t_type', 'user', 'group')  # фильтры тип, пользователь, группа


# UserGroup
@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')  # колонки
    search_fields = ('name',)  # поиск по имени


# UserGroupMember
@admin.register(UserGroupMember)
class UserGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')  # колонки
    list_filter = ('role', 'group')  # фильтры по роль и группе
