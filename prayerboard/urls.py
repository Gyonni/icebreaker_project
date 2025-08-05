from django.urls import path
from . import views

app_name = 'prayerboard'

urlpatterns = [
    path('', views.prayer_board_view, name='board'),
    path('add/', views.add_prayer_request, name='add'),
    # [새로운 기능] 특정 기도제목을 삭제하는 URL 추가
    path('delete/<int:pk>/', views.delete_prayer_request, name='delete'),
    path('api/requests/', views.get_prayer_requests_api, name='api_get_requests'),
]