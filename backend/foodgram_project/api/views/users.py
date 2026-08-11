from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.users import (
    SetAvatarSerializer,
    SetPasswordSerializer,
    UserCreateSerialier,
    UserSeriaizer,
    UserWithRecipesSerializer,
)

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Вьюсет пользователей: регистрация, список, профиль, текущий пользователь,
    аватар, пароль.
    """

    queryset = User.objects.all()

    def get_serializer_type(self):
        if self.action == 'create':
            return UserCreateSerialier
        if self.action == 'subscriptions':
            return UserWithRecipesSerializer
        return UserSeriaizer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post', 'delete',],
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request):
        if request.method == 'POST':
            serializer = SetAvatarSerializer(
                request.user,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(
            serializer.validated_data['new_password']
        )
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = request.user.following_all()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            return Response(
                UserWithRecipesSerializer(author).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            return Response(
                UserWithRecipesSerializer(author).data,
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
