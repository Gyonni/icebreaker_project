from django.urls import path
from . import views

app_name = 'prayerboard'

urlpatterns = [
    path('', views.prayer_board_view, name='board'),
    path('add/', views.add_prayer_request, name='add'),
    path('api/requests/', views.get_prayer_requests_api, name='api_get_requests'),
]