from django import forms
from .models import Review, ReviewMedia
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Profile

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
        fields = ['guest_name', 'text', 'rating']
        widgets = {
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