from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models

class CarDealer(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Название салона")
    location = models.CharField(max_length=200, verbose_name="Адрес")
    contact_number = models.CharField(max_length=15, verbose_name="Телефон")
    email_address = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Автосалон "
        verbose_name_plural = "Автосалоны "
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField('Имя гостя', max_length=100, blank=True, null=True)
    car_dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE, related_name='reviews',verbose_name="Автосалон",null=True)
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


class CarOrder(models.Model):
    COUNTRY_CHOICES = [
        ('Япония', 'Япония'),
        ('Корея', 'Корея'),
        ('Китай', 'Китай'),
    ]

    # Связь с пользователем
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='car_orders',
        null=True,  # Временно, для существующих записей
        blank=True
    )

    # Информация об авто
    country = models.CharField(
        'Страна',
        max_length=20,
        choices=COUNTRY_CHOICES
    )
    brand = models.CharField(
        'Марка авто',
        max_length=100
    )
    year_from = models.PositiveIntegerField(
        'Год от',
        null=True,
        blank=True,
        validators=[MinValueValidator(1990)]
    )
    year_to = models.PositiveIntegerField(
        'Год до',
        null=True,
        blank=True,
        validators=[MinValueValidator(1990)]
    )
    budget_from = models.DecimalField(
        'Бюджет от (USD)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    budget_to = models.DecimalField(
        'Бюджет до (USD)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Контактная информация
    name = models.CharField(
        'Имя',
        max_length=100
    )
    email = models.EmailField(
        'Email'
    )
    phone = models.CharField(
        'Телефон',
        max_length=20
    )
    comments = models.TextField(
        'Дополнительные пожелания',
        blank=True
    )

    # Метаданные
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    is_processed = models.BooleanField(
        'Обработано',
        default=False
    )

    class Meta:
        verbose_name = 'Заявка на авто'
        verbose_name_plural = 'Заявки на авто'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} от {self.name} ({self.brand})'

    def clean(self):
        """
        Валидация данных перед сохранением
        """
        super().clean()

        if self.year_from and self.year_to and self.year_from > self.year_to:
            raise ValidationError({
                'year_from': 'Год "от" не может быть больше года "до"'
            })

        if self.budget_from and self.budget_to and self.budget_from > self.budget_to:
            raise ValidationError({
                'budget_from': 'Бюджет "от" не может быть больше бюджета "до"'
            })

        # Дополнительная валидация для новых записей
        if not self.pk:  # Только для новых записей
            if not self.user:
                raise ValidationError({
                    'user': 'Заявка должна быть связана с пользователем'
                })


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