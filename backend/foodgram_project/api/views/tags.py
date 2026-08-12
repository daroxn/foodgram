from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from api.serializers.tags import TagSerializer
from recipes.models import Tag


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для действий над тегами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
