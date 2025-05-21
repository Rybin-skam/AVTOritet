from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.views import LogoutView
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from .forms import UserRegisterForm, CarForm, ReviewForm, ProfileForm
from .models import EmailVerificationToken, Profile, Car, Review, ReviewMedia, Country, City
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from .models import CarOrder
import logging
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
import logging
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ReviewForm, ReviewMediaForm
from django.contrib.auth.decorators import login_required
from .models import Car
from django.core.cache import cache
import json

from .models import CarDealer
from .forms import CarDealerForm

def dealers(request):
    if request.method == 'POST':
        if request.user.is_staff:  # Проверка, что только админ может отправлять форму
            form = CarDealerForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('dealers')
            else:
                return render(request, 'AVTOritetapp/dealers.html', {'dealers': CarDealer.objects.all(), 'form': form})
        else:
            return render(request, 'AVTOritetapp/dealers.html', {'dealers': CarDealer.objects.all(), 'form': CarDealerForm()})
    else:
        form = CarDealerForm()

    dealers = CarDealer.objects.all()  # Загружаем все автосалоны
    return render(request, 'AVTOritetapp/dealers.html', {'dealers': dealers, 'form': form})
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review, CarDealer
from .forms import ReviewForm, ReviewMediaForm

def reviews(request):
    reviews = Review.objects.select_related('car_dealer').all().order_by('-created_at')
    review_form = ReviewForm(user=request.user)  # Передаем пользователя в форму
    media_form = ReviewMediaForm()

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, user=request.user)
        media_form = ReviewMediaForm(request.POST, request.FILES)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            if request.user.is_authenticated:
                review.user = request.user
            else:
                review.guest_name = request.POST.get('guest_name', 'Аноним')
            review.save()

            if media_form.is_valid() and request.FILES:
                for file in request.FILES.getlist('file'):
                    ReviewMedia.objects.create(
                        review=review,
                        file=file,
                        description=request.POST.get('description', '')
                    )

            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('reviews')

    return render(request, 'AVTOritetapp/reviews.html', {
        'reviews': reviews,
        'review_form': review_form,
        'media_form': media_form,
        'dealers': CarDealer.objects.all()  # Добавляем автосалоны в контекст
    })


@login_required
def review_list(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'AVTOritetapp/review_list.html', {'reviews': reviews})


@login_required
def add_review(request):
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        media_form = ReviewMediaForm(request.POST, request.FILES)

        if review_form.is_valid():
            # Создаем отзыв, но не сохраняем сразу
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()

            # Если форма медиафайлов корректна, сохраняем медиа
            if media_form.is_valid():
                for file in request.FILES.getlist('file'):
                    ReviewMedia.objects.create(
                        review=review,
                        file=file,
                        description=media_form.cleaned_data['description']
                    )

            messages.success(request, 'Отзыв успешно добавлен!')
            return redirect('review_list')
    else:
        review_form = ReviewForm()
        media_form = ReviewMediaForm()

    return render(request, 'AVTOritetapp/add_review.html', {
        'review_form': review_form,
        'media_form': media_form
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Проверка прав: пользователь может редактировать свой отзыв, админ — любой
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете редактировать чужой отзыв.')
        return redirect('reviews')

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, instance=review)
        media_form = ReviewMediaForm(request.POST, request.FILES)

        if review_form.is_valid():
            review_form.save()

            # Обработка медиафайлов, если форма валидна
            if media_form.is_valid():
                if request.FILES:
                    for file in request.FILES.getlist('file'):
                        ReviewMedia.objects.create(
                            review=review,
                            file=file,
                            description=media_form.cleaned_data.get('description', '')
                        )

            messages.success(request, 'Отзыв успешно обновлён!')
            return redirect('reviews')
    else:
        review_form = ReviewForm(instance=review)
        media_form = ReviewMediaForm()

    return render(request, 'AVTOritetapp/edit_review.html', {
        'review_form': review_form,
        'media_form': media_form,
        'review': review
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Проверяем, может ли пользователь удалить отзыв
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, 'Вы не можете удалить чужой отзыв.')
        return redirect('reviews')

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв успешно удалён!')
        return redirect('reviews')

    # Если метод не POST, показываем страницу подтверждения
    return render(request, 'reviews/confirm_delete.html', {'review': review})

def index(request):
    return render(request, 'AVTOritetapp/index.html')

def about(request):
    return render(request, 'AVTOritetapp/about.html')

def contacts(request):
    return render(request, 'AVTOritetapp/contacts.html')

def contact_form(request):
    return render(request, 'AVTOritetapp/contact_form.html')


@cache_page(15)
def catalog(request):
    country = request.GET.get('country', 'japan')
    logger.info(f"Executing catalog view with country: {country}")
    cars = list(Car.objects.filter(country=country))
    return render(request, 'AVTOritetapp/catalog.html', {'cars': cars, 'country': country})


@staff_member_required  # Только для администраторов
def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog')
    else:
        form = CarForm()
    return render(request, 'AVTOritetapp/add_car.html', {'form': form})


def country_detail(request, country_id):
    country = Country.objects.get(id=country_id)
    cars = country.cars.all()  # Получаем все автомобили для выбранной страны
    return render(request, 'AVTOritetapp/country_detail.html', {'country': country, 'cars': cars})

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя, но не активируем сразу
            user = form.save(commit=False)
            user.is_active = False  # Пользователь неактивен до подтверждения email
            user.save()

            # Создаем токен подтверждения
            token = EmailVerificationToken.generate_token_for_user(user)

            # Формируем ссылку подтверждения
            verify_url = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': token.token}))

            # Отправляем письмо с подтверждением
            send_mail(
                'Подтверждение регистрации на AVTOritet',
                f'Приветствуем, {user.username}!\n\n'
                f'Для завершения регистрации перейдите по ссылке:\n{verify_url}\n\n'
                f'Ссылка действительна в течение 24 часов.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request,
                             'Регистрация почти завершена! '
                             'Проверьте вашу почту для подтверждения email.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'AVTOritetapp/register.html', {'form': form})

@csrf_protect
def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email, is_active=False)
            # Удаляем старый токен, если есть
            EmailVerificationToken.objects.filter(user=user).delete()

            # Создаем новый токен
            token = EmailVerificationToken.generate_token_for_user(user)

            # Формируем ссылку подтверждения
            verify_url = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': token.token}))

            # Отправляем письмо
            send_mail(
                'Повторное подтверждение регистрации',
                f'Для подтверждения email перейдите по ссылке: {verify_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден или уже активирован'},
                                status=400)

def verify_email(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        user = token_obj.user

        # Проверяем, не истек ли срок действия токена (24 часа)
        from django.utils import timezone
        if (timezone.now() - token_obj.created_at).days < 1:
            user.is_active = True
            user.save()
            token_obj.delete()  # Удаляем использованный токен
            messages.success(request, 'Email успешно подтвержден! Теперь вы можете войти.')
        else:
            messages.error(request, 'Срок действия ссылки истёк. Зарегистрируйтесь снова.')
            user.delete()  # Удаляем неактивированного пользователя
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения.')

    return redirect('login')


@login_required
def profile(request):
    # Получаем или создаем профиль, если его нет
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'AVTOritetapp/profile.html', {
        'user': request.user,
        'form': form
    })


def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def get_cities(request):
    country_id = request.GET.get('country_id')
    cities = City.objects.filter(country_id=country_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)

def your_view(request):
    countries = Country.objects.all()
    return render(request, 'your_template.html', {'countries': countries})


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # Очищаем сообщения перед выходом
        storage = get_messages(request)
        for _ in storage:
            pass
        storage.used = True

        # Выполняем стандартный выход
        response = super().dispatch(request, *args, **kwargs)
        return response

    next_page = 'index'  # Указываем, куда перенаправлять после выхода



logger = logging.getLogger(__name__)


def order_form(request):
    # Получаем параметры из URL
    car_model = request.GET.get('car_model', '')
    country = request.GET.get('country', '')
    year_start = request.GET.get('year_start', '')
    year_end = request.GET.get('year_end', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')

    context = {
        'car_model': car_model,
        'country': country,  # Теперь передаем country в контекст
        'year_start': year_start,
        'year_end': year_end,
        'price_min': price_min,
        'price_max': price_max,
    }

    return render(request, 'AVTOritetapp/order_form.html', context)

@login_required
def submit_order(request):
    if request.method == 'POST':
        logger.info("Получены данные: %s", request.POST)

        try:
            order = CarOrder(
                user=request.user,
                country=request.POST['country'],
                brand=request.POST['brand'],
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                year_from=request.POST.get('year_from') or None,
                year_to=request.POST.get('year_to') or None,
                budget_from=request.POST.get('budget_from') or None,
                budget_to=request.POST.get('budget_to') or None,
                comments=request.POST.get('comments', '')
            )
            order.save()

            logger.info("Заявка сохранена, ID: %s", order.id)
            messages.success(request, '✅ Ваша заявка успешно отправлена!')
            return redirect('order_form')

        except Exception as e:
            logger.error("Ошибка сохранения: %s", e)
            messages.error(request, f'❌ Ошибка: {str(e)}')
            return redirect('order_form')

    return redirect('order_form')

def set_theme_cookie(request):
    response = HttpResponse("Тема установлена")
    response.set_cookie('site_theme', 'dark', max_age=365*24*60*60)
    return response

def get_theme(request):
    theme = request.COOKIES.get('site_theme', 'light')
    return render(request, 'page.html', {'theme': theme})