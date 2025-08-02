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
]
