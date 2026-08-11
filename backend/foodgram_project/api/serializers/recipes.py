from rest_framework import serializers

from api.serializers.fields import Base64ImageField
from api.serializers.tags import TagSerializer
from api.serializers.users import UserSerializer
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
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'Ингредиент с таким id не существует'
            )
        return value


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления рецепта."""

    class Meta:
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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shoppint_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def _is_in(self, obj, related_name):
        """Проверяет, связан ли рецепт с текущим Пользователем."""
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False
        return getattr(obj, related_name).filter(
            user=request.user
        ).exists()

    def get_is_favorited(self, obj):
        return self._is_in(obj, 'favorites')

    def get_is_in_shopping_cart(self, obj):
        return self._is_in(obj, 'shopping_cart')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления рецепта."""

    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
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

    def validate_ingredients(self, value):
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
        if not value:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return value

    def create(self, validate_data):
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        recipe = Recipe.objects.create(**validate_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validate_data):
        ingredients = validate_data.pop('ingredients', None)
        tags = validate_data.pop('tags', None)

        for attribute, value in validate_data.items():
            setattr(instance, attribute, value)
        instance.value()

        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            self._set_ingredients(instance, ingredients)
        return instance

    @staticmethod
    def _set_ingredients(recipe, ingredients_data):
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
        return RecipeReadSerializer(instance, contex=self.context).data
