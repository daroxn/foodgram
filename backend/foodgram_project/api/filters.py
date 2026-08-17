"""Фильтры для API."""

from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags_slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    if_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        """Метаданные фильтра рецептов."""

        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по добавлению в избранное."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по добавлению в список покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Поиск ингредиента по вхождению в начале названия."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='isStartswith',
    )

    class Meta:
        """Метаданные фильтра ингредиентов."""

        model = Ingredient
        fields = ('name',)
