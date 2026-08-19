"""Модели для приложения recipes."""

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
    SHORT_CODE_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента для рецепта."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        """Метаданные модели ингредиента."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега для рецепта."""

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='Категория',
    )

    class Meta:
        """Метаданные модели тега."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH, verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
        ],
        verbose_name='Время приготовления (мин)',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    short_code = models.CharField(
        max_length=SHORT_CODE_MAX_LENGTH,
        blank=True,
        default='',
        verbose_name='Короткая ссылка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        """Метаданные модели рецепта."""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('short_code',),
                condition=~models.Q(short_code=''),
                name='unique_non_empty_short_code',
            ),
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель связи рецепта и ингредиента с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT)
        ],
        verbose_name='Количество',
    )

    class Meta:
        """Метаданные модели ингредиента в рецепте."""

        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} — {self.amount}'
