from django.urls import path
from . import views

app_name = 'recreation'

urlpatterns = [
    # 1. 게임 플레이 페이지 (참가자용)
    # 예: /recreation/play/a1b2c3d4.../
    path('play/<uuid:qr_code_id>/', views.play_game_view, name='play_game'),

    # 2. 정답 제출 경로 (참가자용)
    path('submit/<uuid:qr_code_id>/', views.submit_answer_view, name='submit_answer'),

    # 3. QR 코드 이미지만 보여주는 페이지 (관리자용)
    path('room-qr/<uuid:qr_code_id>/', views.generate_room_qr, name='generate_room_qr'),
    
    # --- [새로운 기능] 실시간 점수판을 위한 URL 추가 ---    
    path('scoreboard/', views.scoreboard_view, name='scoreboard'),
    path('api/scores/', views.get_scores_api, name='get_scores_api'),
]