"""Настройки админки для приложения accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка пользователя."""

    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active'
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    ordering = ('id',)
