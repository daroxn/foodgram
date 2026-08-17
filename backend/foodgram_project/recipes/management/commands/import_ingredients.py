import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиентов."""

    def add_arguments(self, parser):
        """Добавить аргумент пути к JSON-файлу."""
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Путь к JSON-файлу с ингредиентами.'
        )

    def handle(self, *args, **options):
        """Импортировать ингредиенты из JSON-файла в базу данных."""
        default_path = (
            settings.BASE_DIR.parent.parent / 'data' / 'ingredients.json'
        )
        file_path = Path(options['path']) if options['path'] else default_path

        if not file_path.exists():
            self.stderr.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
            return

        with open(file_path, encoding='utf-8') as file:
            data = json.load()

        ingredients = [
            Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit'],
            )
            for item in data
        ]

        created = Ingredient.objects.bulk_create(
            ingredients,
            ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт завершен. Обработано записей {len(data)}.'
                f'Добавлено новых: {len(created)}.'
            )
        )
