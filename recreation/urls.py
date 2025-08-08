from django.urls import path
from . import views

app_name = 'recreation'

urlpatterns = [
    # 1. QR 스캔 시 처음 접속하는 페이지 (팀 인증)
    # 예: /recreation/play/a1b2c3d4.../
    path('play/<uuid:qr_code_id>/', views.play_game_view, name='play_game'),

    # 2. 문제에 대한 정답을 제출하는 경로
    # 예: /recreation/submit/a1b2c3d4.../
    path('submit/<uuid:qr_code_id>/', views.submit_answer_view, name='submit_answer'),
]