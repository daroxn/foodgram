"""Команда импорта тегов из JSON."""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """Команда для импорта тегов."""

    def add_arguments(self, parser):
        """Добавить аргумент пути к JSON-файлу."""
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Путь к JSON-файлу с тегами.'
        )

    def handle(self, *args, **options):
        """Импортировать теги из JSON-файла в базу данных."""
        if options['path']:
            candidates = [Path(options['path'])]
        else:
            candidates = [
                # Путь для Docker-контейнера (том смонтирован в BASE_DIR/data)
                settings.BASE_DIR / 'data' / 'tags.json',
                # Путь при локальном запуске из исходников репозитория
                settings.BASE_DIR.parent.parent / 'data' / 'tags.json',
            ]

        file_path = next((p for p in candidates if p.exists()), None)

        if file_path is None:
            self.stderr.write(
                self.style.ERROR(
                    'Файл не найден. Проверены пути: '
                    + ', '.join(str(p) for p in candidates)
                )
            )
            return

        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        tags = [
            Tag(
                name=item['name'],
                slug=item['slug'],
            )
            for item in data
        ]

        created = Tag.objects.bulk_create(
            tags,
            ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт завершен. Обработано записей {len(data)}. '
                f'Добавлено новых: {len(created)}.'
            )
        )
