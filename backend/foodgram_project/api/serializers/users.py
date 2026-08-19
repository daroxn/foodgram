"""Сериализаторы пользователей."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers.fields import Base64ImageField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор Пользователя на чтение."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)

    class Meta:
        """Метаданные сериализатора пользователя."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки текущего пользователя на объект."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.subscribers.filter(user=request.user).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации Пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        """Метаданные сериализатора регистрации."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        """Создание пользователя с хэшированием пароля."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор Пользователя с рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta(UserSerializer.Meta):
        """Метаданные сериализатора пользователя с рецептами."""

        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Список рецептов пользователя с учётом лимита."""
        from api.serializers.recipes import RecipeMinifieldSerializer

        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeMinifieldSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class SetAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор загрузки аватара Пользователя."""

    avatar = Base64ImageField()

    class Meta:
        """Метаданные сериализатора аватара."""

        model = User
        fields = ('avatar',)


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля Пользователя."""

    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        """Проверка корректности текущего пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль неверный.')
        return value
