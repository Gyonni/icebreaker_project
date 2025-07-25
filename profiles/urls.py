from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('<uuid:pk>/', views.profile_detail, name='profile_detail'),
    path('<uuid:pk>/qr/', views.generate_qr, name='generate_qr'),
    path('<uuid:pk>/claim/', views.claim_profile, name='claim_profile'),
    path('<uuid:pk>/add/', views.add_scanned_person, name='add_scanned_person'),
    # 프로필 수정 페이지를 위한 URL 추가
    path('<uuid:pk>/edit/', views.profile_edit, name='profile_edit'),
]
