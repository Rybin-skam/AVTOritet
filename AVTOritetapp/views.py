from django.shortcuts import render
from .models import Country, Car
from django.http import HttpResponse

def index(request):
    return render(request, 'AVTOritetapp/index.html')

def about(request):
    return render(request, 'AVTOritetapp/about.html')

def reviews(request):
    return render(request, 'AVTOritetapp/reviews.html')

def contacts(request):
    return render(request, 'AVTOritetapp/contacts.html')

def contact_form(request):
    return render(request, 'AVTOritetapp/contact_form.html')

def login(request):
    return render(request, 'AVTOritetapp/login.html')

def catalog(request):
    countries = Country.objects.all()  # Получаем все страны из базы данных
    return render(request, 'AVTOritetapp/catalog.html', {'countries': countries})

def country_detail(request, country_id):
    country = Country.objects.get(id=country_id)
    cars = country.cars.all()  # Получаем все автомобили для выбранной страны
    return render(request, 'AVTOritetapp/country_detail.html', {'country': country, 'cars': cars})
