# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # jusarangxjesusvision.kr/
    path('', views.index, name='index'),
    # jusarangxjesusvision.kr/schedule/
    path('schedule/', views.schedule, name='schedule'),
    path('homepage-qr/', views.generate_homepage_qr, name='homepage_qr'),
]
