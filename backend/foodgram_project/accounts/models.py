"""Модели для приложения accounts."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from constants import (
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_REGEX,
)


class User(AbstractUser):
    """Модель пользователя с авторизацией по email."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        'Никнейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Недопустимые символы в имени пользователя'
            )
        ],
    )
    first_name = models.CharField('Имя', max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME_MAX_LENGTH)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        default='',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        """Метаданные модели пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
