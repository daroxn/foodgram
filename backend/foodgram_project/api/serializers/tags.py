"""Сериализаторы тегов."""

from rest_framework import serializers

from recipes.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        """Метаданные сериализатора тега."""

        model = Tag
        fields = ('id', 'name', 'slug')
