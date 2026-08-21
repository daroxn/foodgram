"""Кастомные права доступа для API."""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только администратору или суперюзеру."""

    def has_permission(self, request, view):
        """Проверка прав на уровне запроса."""
        return request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):
    """Чтение всем, изменение только администраторам."""

    def has_permission(self, request, view):
        """Проверка прав на уровне запроса."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Чтение всем, изменение автору объекта, создание — авторизованным."""

    def has_permission(self, request, view):
        """Проверка прав на уровне запроса."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Проверка прав на уровне объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
