"""Сериализаторы действий пользователя: избранное, корзина, подписки."""

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import serializers

from actions.models import Favorite, ShoppingCart, Subscription

User = get_user_model()


class BaseUserRecipeActionSerializer(serializers.ModelSerializer):
    """Базовый сериализатор связи пользователя и рецепта."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Метаданные базового сериализатора."""

        fields = ('user', 'recipe')

    def to_representation(self, instance):
        """Возвратить короткое представление рецепта."""
        from api.serializers.recipes import RecipeMinifieldSerializer

        return RecipeMinifieldSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(BaseUserRecipeActionSerializer):
    """Сериализатор добавления рецепта в избранное."""

    class Meta(BaseUserRecipeActionSerializer.Meta):
        """Метаданные сериализатора избранного."""

        model = Favorite
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное.',
            )
        ]


class ShoppingCartSerializer(BaseUserRecipeActionSerializer):
    """Сериализатор добавления рецепта в список покупок."""

    class Meta(BaseUserRecipeActionSerializer.Meta):
        """Метаданные сериализатора списка покупок."""

        model = ShoppingCart
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок.',
            )
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на автора."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Метаданные сериализатора подписки."""

        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.',
            )
        ]

    def validate_author(self, value):
        """Проверить, что пользователь не подписывается на себя."""
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return value

    def to_representation(self, instance):
        """Возвратить представление автора с рецептами."""
        from api.serializers.users import UserWithRecipesSerializer

        author = User.objects.annotate(
            recipes_count=Count('recipes')
        ).get(pk=instance.author_id)
        return UserWithRecipesSerializer(author, context=self.context).data
