from .models import Country, Car
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, ReviewMedia
from .forms import ReviewForm, ReviewMediaForm
from django.http import JsonResponse
from .models import Order, User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages



# Обработка проверки email (для AJAX)
def check_email(request):
    email = request.GET.get('email')  # Получаем email, который проверяем
    exists = User.objects.filter(email=email).exists()  # Проверяем, существует ли такой email
    return JsonResponse({'exists': exists})  # Возвращаем ответ в формате JSON

# Обработка создания заказа (для AJAX)
def create_order(request):
    if request.method == 'POST':
        car_model = request.POST.get('car_model')
        customer_name = request.POST.get('customer_name')
        order = Order.objects.create(car_model=car_model, customer_name=customer_name)  # Создаем заказ
        return JsonResponse({'status': 'success', 'order_id': order.id})  # Возвращаем ID нового заказа
    return JsonResponse({'status': 'error'}, status=400)  # Если не POST запрос, возвращаем ошибку


def reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
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
        'media_form': media_form
    })


@login_required
def review_list(request):
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'AVTOritetapp/review_list.html', {'reviews': reviews})


from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ReviewForm, ReviewMediaForm
from django.contrib.auth.decorators import login_required

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
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, instance=review)
        media_form = ReviewMediaForm(request.POST, request.FILES)

        if review_form.is_valid():
            review_form.save()

            if media_form.is_valid() and request.FILES:
                for file in request.FILES.getlist('file'):
                    ReviewMedia.objects.create(
                        review=review,
                        file=file,
                        description=request.POST.get('description', '')
                    )

            messages.success(request, 'Отзыв успешно обновлен!')
            return redirect('review_list')
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
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    messages.success(request, 'Отзыв успешно удален!')
    return redirect('review_list')

def index(request):
    return render(request, 'AVTOritetapp/index.html')

def about(request):
    return render(request, 'AVTOritetapp/about.html')


def contacts(request):
    return render(request, 'AVTOritetapp/contacts.html')

def contact_form(request):
    return render(request, 'AVTOritetapp/contact_form.html')

def catalog(request):
    countries = Country.objects.all()  # Получаем все страны из базы данных
    return render(request, 'AVTOritetapp/catalog.html', {'countries': countries})

def country_detail(request, country_id):
    country = Country.objects.get(id=country_id)
    cars = country.cars.all()  # Получаем все автомобили для выбранной страны
    return render(request, 'AVTOritetapp/country_detail.html', {'country': country, 'cars': cars})

@login_required
def profile_view(request):
    return render(request, 'web/profile.html')

@login_required
def login_view(request):
    return render(request, 'registration/login.html')