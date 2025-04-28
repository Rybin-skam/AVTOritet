from django import forms
from .models import Review, ReviewMedia

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
