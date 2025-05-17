from django.contrib import admin
from .models import Review  # Импортируем модель отзыва

# Регистрируем модель в админке



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'author_name', 'rating', 'created_at']  # Используем author_name как метод
    list_filter = ['rating', 'created_at']
    search_fields = ['text', 'guest_name', 'user__username']

    def author_name(self, obj):
        return obj.get_author_name()  # Вызываем метод модели
    author_name.short_description = 'Автор'