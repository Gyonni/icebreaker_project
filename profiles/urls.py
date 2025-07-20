from django.urls import re_path # path 대신 re_path를 사용합니다.
from . import views

app_name = 'profiles'

urlpatterns = [
    # re_path와 정규표현식을 사용하여 URL 끝의 슬래시(/)가 선택 사항이 되도록 수정합니다.
    # r'^(?P<pk>[0-9a-f-]+)/?$' -> UUID 형식의 pk를 받고, 끝에 /가 있거나 없어도 됩니다.
    
    # 프로필 상세 페이지
    re_path(r'^(?P<pk>[0-9a-f-]+)/?$', views.profile_detail, name='profile_detail'),
    
    # 프로필 수정 페이지
    re_path(r'^(?P<pk>[0-9a-f-]+)/edit/?$', views.profile_edit, name='profile_edit'),
    
    # QR 코드 생성 페이지
    re_path(r'^(?P<pk>[0-9a-f-]+)/qr/?$', views.generate_qr_code, name='generate_qr'),
    
    # 기기 인증 API
    re_path(r'^(?P<pk>[0-9a-f-]+)/auth/?$', views.authenticate_device, name='authenticate_device'),
    
    # 스캔 API
    re_path(r'^scan/(?P<scanned_pk>[0-9a-f-]+)/?$', views.add_scanned_person, name='add_scanned_person'),
]