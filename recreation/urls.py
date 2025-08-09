from django.urls import path, re_path
from . import views

app_name = 'recreation'

urlpatterns = [
    # 1. 게임 플레이 페이지 (참가자용)
    re_path(r'^play/(?P<qr_code_id>[a-f0-9-]+)/?$', views.play_game_view, name='play_game'),

    # 2. 정답 제출 경로 (참가자용)
    re_path(r'^submit/(?P<qr_code_id>[a-f0-9-]+)/?$', views.submit_answer_view, name='submit_answer'),

    # 3. QR 코드 이미지만 보여주는 페이지 (관리자용)
    re_path(r'^room-qr/(?P<qr_code_id>[a-f0-9-]+)/?$', views.generate_room_qr, name='generate_room_qr'),

    # 4. 실시간 점수판 페이지 및 API (관리자용)
    path('scoreboard/', views.scoreboard_view, name='scoreboard'),
    path('api/scores/', views.get_scores_api, name='get_scores_api'),
]