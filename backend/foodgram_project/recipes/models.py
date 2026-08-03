"""Модели для приложения recipes."""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    "Модель ингредиента для рецепта"

    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=128,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name='Ингредиент',
        verbose_name_plural='Ингредиенты'


    def __str__(self):
        return self.name


class Tag(models.Model):
    "Модель тега для рецепта"

    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name='Тег',
        verbose_name_plural='Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    "Модель рецепта"

    name = models.CharField(max_length=256, verbose_name='Название')
    text = models.TextField(verbose_name='Описание рецепта')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/', null=True, blank=True,
        verbose_name='Изображение'
    )
    creating_time = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания'
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='Добавлено в список покупок'
    )
    is_favorited = models.BooleanField(
        verbose_name='Добавлено в избранное'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    "Промежуточная модель связи рецепта и ингредиента с количеством"

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient} — {self.amount}'
