from django.contrib import admin
from django.contrib import admin
from .models import Review, Car, CarOrder, CarDealer  # Combined both imports
from django.contrib import messages

# Регистрируем модель в админке

@admin.register(CarDealer)
class CarDealerAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'contact_number', 'email_address')
    search_fields = ('title', 'location')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'author_name','car_dealer', 'rating', 'created_at']  # Используем author_name как метод
    list_filter = ['rating', 'created_at']
    search_fields = ['text', 'guest_name', 'user__username']

    def author_name(self, obj):
        return obj.get_author_name()  # Вызываем метод модели
    author_name.short_description = 'Автор'

@admin.register(Car)  # Регистрируем Car
class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'country', 'year_start', 'year_end', 'engine_volume', 'price_min', 'price_max', 'photo']  # Все поля
    list_filter = ['country', 'year_start', 'year_end']  # Фильтры по основным полям
    search_fields = ['model', 'country']  # Поиск по ключевым полям


@admin.register(CarOrder)
class CarOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'country', 'created_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Очищаем сообщения в админке
        storage = messages.get_messages(request)
        storage.used = True