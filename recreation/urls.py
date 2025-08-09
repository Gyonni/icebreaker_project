from django.urls import path
from . import views

app_name = 'recreation'
urlpatterns = [
    path('play/<uuid:qr_code_id>/', views.play_game_view, name='play_game'),
    path('submit_answer/', views.submit_answer_view, name='submit_answer'),
    path('room-qr/<uuid:qr_code_id>/', views.generate_room_qr, name='generate_room_qr'),
    path('scoreboard/', views.scoreboard_view, name='scoreboard'),
    path('api/scores/', views.get_scores_api, name='get_scores_api'),
]