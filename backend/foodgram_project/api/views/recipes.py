"""Представления для рецептов."""

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    RecipeMinifieldSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
)
from actions.models import Favorite, ShoppingCart
from recipes.models import Recipe, RecipeIngredient


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецепта."""

    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Возвратить сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """Сохранить рецепт с автором из запроса."""
        serializer.save(author=self.request.user)

    def _add_or_remove_action(self, model, request, obj):
        """Добавить или удалить рецепт из связанного списка."""
        recipe = get_object_or_404(Recipe, pk=obj)
        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(
                    {'errors': 'Рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RecipeMinifieldSerializer(
                recipe, context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

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
        return self._add_or_remove_action(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавить или удалить рецепт из корзины покупок."""
        return self._add_or_remove_action(ShoppingCart, request, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Сформировать и скачать файл списка покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=request.user)
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
        content = '\n'.join(lines)
        response = HttpResponse(
            content, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

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
            {'short_link': short_link}
        )

    @staticmethod
    def _generate_short_code():
        """Сгенерировать уникальный короткий код из трёх символов."""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(3))
            if not Recipe.objects.filter(short_code=code).exists():
                return code


def short_link_redirect(request, code):
    """Редирект при переходе по сокращенной ссылке."""
    recipe = get_object_or_404(Recipe, short_code=code)
    return redirect(f'/recipes/{recipe.id}/')
