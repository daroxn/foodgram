"""Настройки админки для приложения recipes."""

from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin
from django.db.models import Count, Prefetch

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientImage(admin.TabularInline):
    """Отображение ингредиентов внутри рецепта."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_display_links = ('name',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов."""

    list_display = (
        'id',
        'name',
        'slug'
    )
    list_display_links = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        'id',
        'name',
        'author',
        'pub_date',
        'favorites_count'
    )
    list_display_links = ('name', 'author')
    search_fields = ('name',)
    list_filter = (
        AutocompleteFilterFactory('Автор', 'author'),
        AutocompleteFilterFactory('Тег', 'tags'),
        'pub_date',
    )
    inlines = (RecipeIngredientImage,)
    readonly_fields = ('favorites_count',)

    def get_queryset(self, request):
        """Оптимизация запросов для списка рецептов в админке."""
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related(
            'tags',
            Prefetch(
                'recipe_ingredients',
                queryset=RecipeIngredient.objects.select_related(
                    'ingredient'
                ),
            ),
        ).annotate(favorites_count=Count('favorites', distinct=True))

    @admin.display(description='В избранном (раз)', ordering='favorites_count')
    def favorites_count(self, obj):
        """Число добавлений рецепта в избранное."""
        return obj.favorites_count
