"""Представления для рецептов."""

import secrets

from django.db.models import Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers.actions import FavoriteSerializer, ShoppingCartSerializer
from api.serializers.recipes import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
)
from actions.models import Favorite, ShoppingCart
from foodgram_project.constants import (
    SHORT_CODE_ALPHABET,
    SHORT_CODE_LENGTH,
)
from recipes.models import Recipe, RecipeIngredient


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецепта."""

    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        """Возвратить queryset рецептов с аннотациями пользователя."""
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'tags', 'recipe_ingredients__ingredient'
        )
        user = self.request.user
        if not user.is_authenticated:
            return queryset.annotate(
                is_favorited=Value(False),
                is_in_shopping_cart=Value(False),
            )
        return queryset.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=user, recipe=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=user, recipe=OuterRef('pk')
                )
            ),
        )

    def get_serializer_class(self):
        """Возвратить сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохранить рецепт с автором из запроса."""
        serializer.save(author=self.request.user)

    def _add_action(self, serializer_class, request, pk):
        """Добавить рецепт в связанный список через сериализатор."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={'recipe': recipe.pk},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_action(self, model, request, pk):
        """Удалить рецепт из связанного списка."""
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепта не было в списке.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавить или удалить рецепт из избранного."""
        if request.method == 'POST':
            return self._add_action(FavoriteSerializer, request, pk)
        return self._remove_action(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавить или удалить рецепт из корзины покупок."""
        if request.method == 'POST':
            return self._add_action(ShoppingCartSerializer, request, pk)
        return self._remove_action(ShoppingCart, request, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Сформировать и скачать файл списка покупок."""
        content = self._build_shopping_list(request.user)
        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @staticmethod
    def _build_shopping_list(user):
        """Собрать текст списка покупок для пользователя."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )
        lines = ['Список покупок:', '']
        for item in ingredients:
            lines.append(
                f"- {item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total']}"
            )
        return '\n'.join(lines)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Возвратить короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe.short_code:
            recipe.short_code = self._generate_short_code()
            recipe.save(update_fields=['short_code'])
        short_link = request.build_absolute_uri(f'/s/{recipe.short_code}/')
        return Response(
            {'short-link': short_link}
        )

    @staticmethod
    def _generate_short_code():
        """Сгенерировать уникальный короткий код."""
        while True:
            code = ''.join(
                secrets.choice(SHORT_CODE_ALPHABET)
                for _ in range(SHORT_CODE_LENGTH)
            )
            if not Recipe.objects.filter(short_code=code).exists():
                return code


def short_link_redirect(request, code):
    """Редирект при переходе по сокращенной ссылке."""
    recipe = get_object_or_404(Recipe, short_code=code)
    return redirect(f'/recipes/{recipe.id}/')
