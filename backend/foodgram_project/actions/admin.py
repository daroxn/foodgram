"""Настройки админки для приложения actions."""

from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from actions.models import Favorite, ShoppingCart, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка подписок."""

    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('user', 'author')
    list_filter = (
        AutocompleteFilterFactory('Пользователь', 'user'),
        AutocompleteFilterFactory('Автор', 'author'),
    )

    def get_queryset(self, request):
        """Оптимизация запросов: заджойнить пользователя и автора."""
        return super().get_queryset(request).select_related(
            'user', 'author'
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    list_display_links = ('user', 'recipe')
    list_filter = (
        AutocompleteFilterFactory('Пользователь', 'user'),
        AutocompleteFilterFactory('Рецепт', 'recipe'),
    )

    def get_queryset(self, request):
        """Оптимизация запросов: заджойнить пользователя и рецепт."""
        return super().get_queryset(request).select_related(
            'user', 'recipe'
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    list_display_links = ('user', 'recipe')
    list_filter = (
        AutocompleteFilterFactory('Пользователь', 'user'),
        AutocompleteFilterFactory('Рецепт', 'recipe'),
    )

    def get_queryset(self, request):
        """Оптимизация запросов: заджойнить пользователя и рецепт."""
        return super().get_queryset(request).select_related(
            'user', 'recipe'
        )
