from rest_framework import mixins, viewsets

from api.serializers.tags import TagSerializer
from recipes.models import Tag


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для действий над тегами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
