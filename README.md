# Foodgram — продуктовый помощник

Сервис для публикации рецептов, формирования списка покупок и подписки на авторов.

## Технологии

- **Backend:** Django 5.1, Django REST Framework, PostgreSQL, Gunicorn
- **Frontend:** React (SPA, собирается в статические файлы)
- **Инфраструктура:** Docker, Docker Compose, Nginx
- **CI/CD:** GitHub Actions (тесты, сборка и пуш образов, деплой на сервер)

## Запуск проекта в Docker

1. Клонируйте репозиторий и перейдите в директорию `infra`:

   ```bash
   cd infra
   ```

2. Создайте файл `.env` с переменными окружения (пример):

   ```env
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=127.0.0.1,localhost,your-server-ip
   CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost,http://your-server-ip
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=your-password
   DB_HOST=db
   DB_PORT=5432
   ```

3. Запустите контейнеры:

   ```bash
   docker compose -f docker-compose.production.yml up -d --build
   ```

4. Выполните миграции и соберите статику:

   ```bash
   docker compose -f docker-compose.production.yml exec backend python manage.py migrate
   docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
   docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
   ```

## Деплой на сервер

Проект настроен на автоматический деплой через GitHub Actions при пуше в ветку `main`.

Workflow выполняет:
1. Запуск тестов (flake8)
2. Сборку и пуш Docker-образов в Docker Hub
3. Деплой на сервер по SSH (docker compose pull + up -d)

## Адрес сервера

Проект развёрнут по адресу: **http://51.250.32.250:8080**

## Документация API

OpenAPI-схема доступна по адресу `/api/docs/` (ReDoc).

## Структура проекта

```
foodgram/
├── backend/          # Django-проект (API + модели)
├── frontend/         # React-приложение
├── infra/            # Docker Compose файлы для разработки и продакшена
├── data/             # Данные для импорта ингредиентов
├── docs/             # OpenAPI-схема
└── .github/          # GitHub Actions workflows
```
