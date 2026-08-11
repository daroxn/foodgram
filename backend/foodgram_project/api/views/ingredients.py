from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from api.serializers.ingredients import IngredientSerializer
from recipes.models import Ingredient


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для действий над ингредиентами"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
