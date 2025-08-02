from django.urls import path, re_path
from . import views

app_name = 'profiles'

urlpatterns = [
    re_path(r'^(?P<pk>[a-f0-9-]+)/?$', views.profile_detail, name='profile_detail'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/qr/?$', views.generate_qr, name='generate_qr'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/claim/?$', views.claim_profile, name='claim_profile'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/add/?$', views.add_scanned_person, name='add_scanned_person'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/edit/?$', views.profile_edit, name='profile_edit'),
    # [새로운 기능] 3T1L 게임 플레이를 처리할 URL 추가
    re_path(r'^(?P<pk>[a-f0-9-]+)/play_3t1l/?$', views.play_3t1l, name='play_3t1l'),
    # --- [새로운 기능] 빙고 및 사회자 기능 URL 추가 ---
    path('bingo/', views.bingo_board, name='bingo_board'),
    # 사회자만 아는 비밀 주소
    path('moderator/random-picker/', views.random_profile_picker, name='random_picker'),
    # 사회자 페이지에서 다음 사람을 뽑기 위한 API 주소
    path('api/get-random-profile/', views.get_random_profile_data, name='get_random_profile_data'),
]

