from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeShortLinkSerializer,
)
from recipes.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'author',
        'tags',
        'is_favorited',
        'is_in_shopping_cart',
    )

    def get_serializer_type(self):
        """Определяет сериализатор для чтения или записи."""
        if self.action in ('list', 'retrive'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """
        Маршрут для добавления/удаления из избранного.
        POST /api/recipes/{id}/favorite/.
        """
        recipe = get_object_or_404(Recipe, pk=None)
        serializer = RecipeWriteSerializer(recipe)
        if request.method == 'POST':
            return Response(
                serializer.data,
                {'detail': 'Рецепт успешно добавлен в избранное.'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            return Response(
                serializer.data,
                {'detail': 'Рецепт успешно удален из избранного.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """
        Маршрут для добавления/удаления из списка покупок.
        POST/DELETE /api/recipes/{id}/shopping_cart/.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeWriteSerializer(recipe)
        if request.method == 'POST':
            return Response(
                serializer.data,
                {'detail': 'Рецепт успешно добавлен в список покупок.'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            return Response(
                serializer.data,
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )
