from django.urls import path, re_path
from . import views

app_name = 'profiles'

urlpatterns = [
    # re_path와 /?를 사용하여 URL 끝에 슬래시가 있고 없고를 모두 허용합니다.
    re_path(r'^(?P<pk>[a-f0-9-]+)/?$', views.profile_detail, name='profile_detail'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/qr/?$', views.generate_qr, name='generate_qr'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/claim/?$', views.claim_profile, name='claim_profile'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/add/?$', views.add_scanned_person, name='add_scanned_person'),
    re_path(r'^(?P<pk>[a-f0-9-]+)/edit/?$', views.profile_edit, name='profile_edit'),
]
