"""Сериализаторы ингредиентов."""

from rest_framework import serializers

from recipes.models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        """Метаданные сериализатора ингредиента."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
