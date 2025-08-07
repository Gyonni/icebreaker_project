from django.urls import path
from . import views

app_name = 'recreation'

urlpatterns = [
    # 예: /recreation/play/a1b2c3d4.../
    path('play/<uuid:qr_code_id>/', views.play_game_view, name='play_game'),
]