from .models import Country, Car
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review, ReviewMedia
from .forms import ReviewForm, ReviewMediaForm
from django.http import JsonResponse
from .models import Order, User
from django.contrib.auth import authenticate, login as auth_login
from .forms import UserRegisterForm
from .models import City  # Импортируем модель City
from .models import Country



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

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} создан! Теперь войдите.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'AVTOritetapp/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'AVTOritetapp/profile.html')

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