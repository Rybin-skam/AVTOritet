
from django import forms
from .models import Review, ReviewMedia, Car, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import CarDealer

class CarDealerForm(forms.ModelForm):
    class Meta:
        model = CarDealer
        fields = ['title', 'location', 'contact_number', 'email_address']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название салона'}),
            'location': forms.TextInput(attrs={'placeholder': 'Адрес'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Телефон'}),
            'email_address': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
class ReviewMediaForm(forms.ModelForm):
    class Meta:
        model = ReviewMedia
        fields = ['file', 'description']

# Создаём FormSet для обработки нескольких медиафайлов
ReviewMediaFormSet = inlineformset_factory(
    Review,  # Модель родителя
    ReviewMedia,  # Модель связанных объектов
    form=ReviewMediaForm,  # Форма для каждого медиа
    extra=1,  # Количество пустых форм для добавления
    can_delete=True,  # Разрешить удаление
    max_num=5  # Максимальное количество медиафайлов (опционально)
)
class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['country', 'model', 'photo', 'year_start', 'year_end', 'engine_volume', 'price_min', 'price_max']
class ReviewForm(forms.ModelForm):
    guest_name = forms.CharField(
        label='Ваше имя',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Представьтесь...'
        })
    )

    class Meta:
        model = Review
        fields = ['guest_name', 'car_dealer','text', 'rating']
        widgets = {
            'car_dealer': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите ваш отзыв...',
                'rows': 4
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['guest_name'].widget = forms.HiddenInput()


class ReviewMediaForm(forms.ModelForm):
    class Meta:
        model = ReviewMedia
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Описание файла...'
            })
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Электронная почта',
        required=True,  # Явно указываем, что поле обязательно
        help_text="На этот email будет отправлено письмо с подтверждением"  # Добавляем подсказку
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переопределяем сообщения валидации (оставляем ваше текущее форматирование)
        self.fields['password1'].help_text = _(
            "• Ваш пароль не должен быть слишком похож на другую личную информацию.<br>"
            "• Ваш пароль должен содержать как минимум 8 символов.<br>"
            "• Пароль не должен быть слишком простым и распространённым.<br>"
            "• Пароль не может состоять только из цифр."
        )
        self.fields['password2'].label = "Подтверждение пароля"
        self.fields['password2'].help_text = _("Для подтверждения введите, пожалуйста, пароль ещё раз.")

    def clean_email(self):
        """Проверяем, что email уникален"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Этот email уже зарегистрирован. "
                "Используйте другой email или восстановите пароль, если это ваш аккаунт."
            )
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'gender', 'birth_date', 'country']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Можно добавить кастомные атрибуты или валидацию здесь