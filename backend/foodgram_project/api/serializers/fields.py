"""Кастомные поля сериализаторов."""

import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в формате Base64."""

    def to_internal_value(self, data):
        """Декодирование изображения из Base64."""
        if isinstance(data, str) and data.startswith('data:image'):
            format_value, base64_value = data.split(';base64,')
            extention = format_value.split('/')[-1]
            file_name = f'{uuid.uuid4()}.{extention}'
            data = ContentFile(base64.b64decode(base64_value), name=file_name)
        return super().to_internal_value(data)
