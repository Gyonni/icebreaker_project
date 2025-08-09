from django.urls import path
from . import views

app_name = 'recreation'

urlpatterns = [
    # 게임 플레이를 위한 임시 URL. 나중에 완성합니다.
    path('play/<uuid:qr_code_id>/', views.play_game_view, name='play_game'),
]