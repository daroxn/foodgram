"""Настройки админки для приложения actions."""

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
    search_fields = (
        'user__username',
        'author__username'
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'recipe__name'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'recipe__name'
    )
