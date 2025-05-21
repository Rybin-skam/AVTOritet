from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dealers/', views.dealers, name='dealers'),
    path('catalog/', views.catalog, name='catalog'),
    path('add_car/', views.add_car, name='add_car'),
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews, name='reviews'),
    path('contacts/', views.contacts, name='contacts'),
    path('contact_form/', views.contact_form, name='contact_form'),
    path('country/<int:country_id>/', views.country_detail, name='country_detail'),
    path('reviews/my/', views.review_list, name='review_list'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('login/', auth_views.LoginView.as_view(template_name='AVTOritetapp/login.html'), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('profile/', views.profile, name='profile'),
    path('check_username/', views.check_username, name='check_username'),
    path('get_cities/', views.get_cities, name='get_cities'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
