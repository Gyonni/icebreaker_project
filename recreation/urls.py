from django.urls import path
from . import views

app_name = 'recreation'

urlpatterns = [
    # 기존 게임 플레이 페이지 URL
    path('play/<uuid:qr_code_id>/', views.play_game_view, name='play_game'),

    # --- [새로운 기능] QR 코드 이미지만 보여주는 페이지 URL 추가 ---
    path('room-qr/<uuid:qr_code_id>/', views.generate_room_qr, name='generate_room_qr'),
]