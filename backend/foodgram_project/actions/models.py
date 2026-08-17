"""Модели для приложения actions."""

from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()


class Subscription(models.Model):
    """Модель подписки одного пользователя на другого."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        """Метаданные модели подписки."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('author')),
                name='prevent_self_subscription',
            ),
        ]

    def __str__(self):
        """Строковое представление подписки."""
        return f'{self.user} - {self.author}'


class Favorite(models.Model):
    """Модель рецепта, добавленного в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        """Метаданные модели избранного."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        """Строковое представление избранного."""
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель рецепта, добавленного в список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        """Метаданные модели списка покупок."""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            ),
        ]

    def __str__(self):
        """Строковое представление списка покупок."""
        return f'{self.user} - {self.recipe}'
