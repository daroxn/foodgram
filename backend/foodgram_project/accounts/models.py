from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя с авторизацией по email."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=256,
        unique=True,
    )
    username = models.CharField(
        'Никнейм',
        max_length=100,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Недопустимые символы в имени пользователя'
            )
        ],
    )
    first_name = models.CharField('Имя', max_length=256)
    last_name = models.CharField('Фамилия', max_length=256)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        null=True,
        blank=True,
        default='',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
