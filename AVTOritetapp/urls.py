from django.urls import path
from . import views  # Импортируем наши представления (views)

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('catalog/', views.catalog, name='catalog'),  # Страница каталога
    path('about/', views.about, name='about'),  # Страница "О нас"
    path('reviews/', views.reviews, name='reviews'),  # Страница отзывов
    path('contacts/', views.contacts, name='contacts'),  # Страница контактов
    path('contact_form/', views.contact_form, name='contact_form'),  # Форма для связи
    path('login/', views.login_view, name='login'),  # Страница для входа
    path('country/<int:country_id>/', views.country_detail, name='country_detail'),
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/my/', views.review_list, name='review_list'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('check_email/', views.check_email, name='check_email'),  # Проверка email
    path('create_order/', views.create_order, name='create_order'),  # Создание заказа
    path('profile/', views.profile_view, name='profile'),

]
