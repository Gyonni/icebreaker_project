from django.urls import path
from . import views

app_name = 'profiles'
urlpatterns = [
    path('<uuid:pk>/', views.profile_view, name='profile_detail'),
    path('<uuid:pk>/qr/', views.generate_qr_code, name='generate_qr'),
    path('<uuid:pk>/authenticate/', views.authenticate_device, name='authenticate_device'),
    path('scan/<uuid:scanned_pk>/', views.add_scanned_person, name='add_scanned'),
    # ★★★★★ 프로필 수정 URL 추가 ★★★★★
    path('edit/', views.edit_profile, name='edit_profile'),
]
