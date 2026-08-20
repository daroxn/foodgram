"""Команда наполнения базы тестовыми данными для ревью."""

import io
import random

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from PIL import Image

from actions.models import Favorite, Subscription
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()

TEST_USERS = (
    {
        'username': 'test_user1',
        'email': 'test_user1@example.com',
        'first_name': 'Иван',
        'last_name': 'Петров',
    },
    {
        'username': 'test_user2',
        'email': 'test_user2@example.com',
        'first_name': 'Анна',
        'last_name': 'Смирнова',
    },
    {
        'username': 'test_user3',
        'email': 'test_user3@example.com',
        'first_name': 'Сергей',
        'last_name': 'Иванов',
    },
)
TEST_PASSWORD = 'TestPass123'

RECIPE_NAMES = (
    'Борщ украинский',
    'Оливье классический',
    'Плов с курицей',
    'Сырники со сметаной',
    'Блины на молоке',
    'Паста карбонара',
    'Греческий салат',
    'Тирамису',
    'Куриный суп с лапшой',
    'Драники картофельные',
)
RECIPE_TEXT = (
    'Вкусный и простой рецепт, проверенный временем. '
    'Отлично подойдет для всей семьи.'
)


class Command(BaseCommand):
    """Команда для наполнения базы тестовыми данными."""

    def add_arguments(self, parser):
        """Добавить аргументы количества рецептов и избранного."""
        parser.add_argument(
            '--recipes',
            type=int,
            default=7,
            help='Количество рецептов для создания (минимум 7).',
        )
        parser.add_argument(
            '--favorites',
            type=int,
            default=2,
            help='Количество записей избранного (минимум 2).',
        )

    def handle(self, *args, **options):
        """Наполнить базу тестовыми пользователями и рецептами."""
        recipes_count = max(options['recipes'], 7)
        favorites_count = max(options['favorites'], 2)

        with transaction.atomic():
            users = self._create_users()
            tags = list(Tag.objects.all())
            ingredients = list(Ingredient.objects.all())

            if not tags:
                self.stderr.write(self.style.ERROR(
                    'В базе нет тегов. Сначала выполните '
                    '"python manage.py import_tags".'
                ))
                return
            if not ingredients:
                self.stderr.write(self.style.ERROR(
                    'В базе нет ингредиентов. Сначала выполните '
                    '"python manage.py import_ingredients".'
                ))
                return

            recipes = self._create_recipes(
                recipes_count, users, tags, ingredients
            )
            self._create_subscriptions(users)
            self._create_favorites(favorites_count, users, recipes)

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Пользователей: {len(users)}, '
            f'рецептов: {len(recipes)}.'
        ))

    def _create_users(self):
        """Создать тестовых пользователей."""
        users = []
        for data in TEST_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                },
            )
            if created:
                user.set_password(TEST_PASSWORD)
                user.save(update_fields=['password'])
            users.append(user)
        return users

    def _generate_image(self, name):
        """Сгенерировать изображение-заглушку для рецепта."""
        color = tuple(random.randint(0, 255) for _ in range(3))
        image = Image.new('RGB', (200, 200), color)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        return ContentFile(buffer.getvalue(), name=f'{name}.jpg')

    def _create_recipes(self, count, users, tags, ingredients):
        """Создать тестовые рецепты со случайными тегами и ингредиентами."""
        recipes = []
        for i in range(count):
            name = f'{random.choice(RECIPE_NAMES)} №{i + 1}'
            author = users[i % len(users)]
            recipe = Recipe.objects.create(
                name=name,
                text=RECIPE_TEXT,
                author=author,
                cooking_time=random.randint(5, 120),
                image=self._generate_image(f'recipe_{i + 1}'),
            )
            recipe.tags.set(
                random.sample(tags, k=min(2, len(tags)))
            )
            for ingredient in random.sample(
                ingredients, k=min(3, len(ingredients))
            ):
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=random.randint(1, 500),
                )
            recipes.append(recipe)
        return recipes

    def _create_subscriptions(self, users):
        """Создать тестовые подписки между пользователями."""
        if len(users) < 2:
            return
        for user, author in zip(users, users[1:] + users[:1]):
            try:
                Subscription.objects.get_or_create(
                    user=user, author=author
                )
            except IntegrityError:
                continue

    def _create_favorites(self, count, users, recipes):
        """Создать тестовые записи избранного."""
        created = 0
        attempts = 0
        while created < count and attempts < count * 10:
            attempts += 1
            user = random.choice(users)
            recipe = random.choice(recipes)
            _, is_new = Favorite.objects.get_or_create(
                user=user, recipe=recipe
            )
            if is_new:
                created += 1
