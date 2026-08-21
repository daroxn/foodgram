"""Пагинация для API."""

from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Пагинация с возможностью изменить размер страницы через `limit`."""

    page_size_query_param = 'limit'
