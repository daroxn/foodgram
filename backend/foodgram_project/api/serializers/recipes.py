"""Сериализаторы рецептов."""

from rest_framework import serializers

from api.serializers.fields import Base64ImageField
from api.serializers.tags import TagSerializer
from api.serializers.users import UserSerializer
from foodgram_project.constants import MIN_INGREDIENT_AMOUNT
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        """Метаданные сериализатора ингредиента в рецепте."""

        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Сериализатор ингредиента при создании/обновлении рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    def validate_id(self, value):
        """Проверить существование ингредиента по ID."""
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'Ингредиент с таким id не существует'
            )
        return value


class RecipeMinifieldSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления рецепта."""

    class Meta:
        """Метаданные сериализатора короткого представления рецепта."""

        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения Рецепта."""

    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        read_only=True,
        many=True,
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        """Метаданные сериализатора чтения рецепта."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления рецепта."""

    ingredients = RecipeIngredientWriteSerializer(
        many=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    image = Base64ImageField(required=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        """Метаданные сериализатора создания/обновления рецепта."""

        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'cooking_time',
            'ingredients',
            'tags',
            'author',
        )

    def validate(self, attrs):
        """Проверить наличие обязательных полей при частичном обновлении."""
        if self.partial:
            if 'ingredients' not in self.initial_data:
                raise serializers.ValidationError(
                    {'ingredients': 'Это поле обязательно.'}
                )
            if 'tags' not in self.initial_data:
                raise serializers.ValidationError(
                    {'tags': 'Это поле обязательно.'}
                )
        return attrs

    def validate_ingredients(self, value):
        """Проверить список ингредиентов на пустоту и дубликаты."""
        if not value:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def validate_tags(self, value):
        """Проверить список тегов на пустоту и дубликаты."""
        if not value:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return value

    def create(self, validated_data):
        """Создать рецепт с ингредиентами и тегами."""
        ingredients, tags = self._pop_ingredients_and_tags(validated_data)
        recipe = Recipe.objects.create(**validated_data)
        self._set_tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновить рецепт с ингредиентами и тегами."""
        ingredients, tags = self._pop_ingredients_and_tags(validated_data)
        instance = super().update(instance, validated_data)
        self._set_tags_and_ingredients(instance, tags, ingredients)
        return instance

    @staticmethod
    def _pop_ingredients_and_tags(validated_data):
        """Извлечь из данных списки ингредиентов и тегов."""
        return (
            validated_data.pop('ingredients'),
            validated_data.pop('tags'),
        )

    @staticmethod
    def _set_tags_and_ingredients(recipe, tags, ingredients_data):
        """Заменить теги и ингредиенты рецепта на новые."""
        recipe.tags.set(tags)
        recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=item['id']),
                amount=item['amount'],
            )
            for item in ingredients_data
        ])

    def to_representation(self, instance):
        """Возвратить полное представление рецепта."""
        return RecipeReadSerializer(instance, context=self.context).data
