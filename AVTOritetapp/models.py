from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        return self.user.username if self.user else self.guest_name or "Аноним"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв от {self.get_author_name()}'

class ReviewMedia(models.Model):
    review = models.ForeignKey(Review, related_name='media', on_delete=models.CASCADE)
    file = models.FileField('Медиафайл', upload_to='reviews/media/%Y/%m/%d/', blank=True, null=True)
    description = models.CharField('Описание', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Медиа отзыва'
        verbose_name_plural = 'Медиа отзывов'

    def __str__(self):
        return f"Медиа для отзыва {self.review.id} - {self.description or 'Без описания'}"

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


# Выбор страны
COUNTRY_CHOICES = (
    ('japan', 'Япония'),
    ('china', 'Китай'),
    ('korea', 'Корея'),
)

class Car(models.Model):
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES)
    model = models.CharField(max_length=100)  # Название модели авто
    photo = models.ImageField(upload_to='cars/photos/', null=True, blank=True)  # Фото
    year_start = models.IntegerField(null=True)  # Начало выпуска
    year_end = models.IntegerField(null=True, blank=True)  # Конец выпуска (опционально)
    engine_volume = models.FloatField(null=True)  # Объём двигателя (литры)
    price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Минимальная цена
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Максимальная цена
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.get_country_display()} - {self.model}"

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"


class Order(models.Model):
    car_model = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.car_model}"

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_token_for_user(cls, user):
        token = get_random_string(64)
        return cls.objects.create(user=user, token=token)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    GENDER_CHOICES = (
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    birth_date = models.DateField(null=True, blank=True)

    COUNTRY_CHOICES = (
        ('RU', 'Россия'),
        ('KZ', 'Казахстан'),
        ('BY', 'Беларусь'),
        # добавьте другие страны по необходимости
    )
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)


# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()