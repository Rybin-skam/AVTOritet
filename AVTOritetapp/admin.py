from django.contrib import admin
from .models import Review  # Импортируем модель отзыва

# Регистрируем модель в админке
admin.site.register(Review)
