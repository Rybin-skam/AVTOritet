from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField('Имя гостя', max_length=100, blank=True, null=True)
    text = models.TextField('Текст отзыва')
    rating = models.IntegerField(
        'Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    def get_author_name(self):
        return self.user.username if self.user else self.guest_name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв от {self.user.username}'

class ReviewMedia(models.Model):
    review = models.ForeignKey(Review, related_name='media', on_delete=models.CASCADE)
    file = models.FileField('Медиафайл', upload_to='reviews/media/')
    description = models.CharField('Описание', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Медиа отзыва'
        verbose_name_plural = 'Медиа отзывов'

class Country(models.Model):
    name = models.CharField(max_length=100)  # Название страны
    description = models.TextField()  # Описание страны
    image = models.ImageField(upload_to='countries/', null=True, blank=True)  # Изображение страны

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название города")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")

    def __str__(self):
        return self.name


class Car(models.Model):
    country = models.ForeignKey(Country, related_name='cars', on_delete=models.CASCADE)  # Связь с моделью Country
    model_name = models.CharField(max_length=100)  # Название модели авто
    year = models.IntegerField()  # Год выпуска
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена авто
    image = models.ImageField(upload_to='cars/', null=True, blank=True)  # Изображение авто

    def __str__(self):
        return f"{self.model_name} ({self.year})"

class Order(models.Model):
    car_model = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.car_model}"