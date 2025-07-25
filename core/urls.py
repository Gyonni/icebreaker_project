# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # jusarangxjesusvision.kr/
    path('', views.index, name='index'),
    # jusarangxjesusvision.kr/schedule/
    path('schedule/', views.schedule, name='schedule'),
]
