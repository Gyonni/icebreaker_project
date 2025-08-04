from django.urls import path, re_path
from . import views

app_name = 'profiles'

urlpatterns = [
    # 빙고 및 사회자 기능 URL
    path('bingo/', views.bingo_board, name='bingo_board'),
    path('bingo/shuffle/', views.shuffle_bingo_board, name='shuffle_bingo_board'),
    path('moderator/random-picker/', views.random_profile_picker, name='random_picker'),
    path('api/get-random-profile/', views.get_random_profile_data, name='get_random_profile_data'),
    path('moderator/reset-picks/', views.reset_all_picks, name='reset_all_picks'),

    # 개별 프로필 URL
    re_path(r'^(?P<pk>[a-f0-9-]+)/?$', views.profile_detail, name='profile_detail'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/qr/?$', views.generate_qr, name='generate_qr'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/claim/?$', views.claim_profile, name='claim_profile'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/add/?$', views.add_scanned_person, name='add_scanned_person'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/edit/?$', views.profile_edit, name='profile_edit'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/play_3t1l/?$', views.play_3t1l, name='play_3t1l'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/recommend_tmi/?$', views.recommend_tmi, name='recommend_tmi'),
]
